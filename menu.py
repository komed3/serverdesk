#!/usr/bin/env python3

# --------------------------------------------------------------------------------
# ServerDesk
# 
# Simple monitoring and control menu for servers using a touch screen.
# Can be used to run commands, open applications, or display information.
# 
# Author: Paul Köhler (komed3)
# License: MIT
# --------------------------------------------------------------------------------

import evdev # type: ignore
import json
import os
import signal
import subprocess
import time

from PIL import Image # type: ignore

# Paths
SRC_PATH = os.path.dirname( os.path.realpath( __file__ ) )
CFG_PATH = os.path.join( SRC_PATH, 'cfg' )
BIN_PATH = os.path.join( SRC_PATH, 'bin' )
IMG_PATH = os.path.join( SRC_PATH, 'assets' )

# Constants
TERM = os.getenv( 'TERM' ) or 'linux'
IMAGE = os.path.join( IMG_PATH, 'menu.png' )

# Display
TOUCH_DEVICE = '/dev/input/event3'
FRAMEBUFFER = '/dev/fb0'
TOUCH_RES_X = 4096          # Touch resolution in X direction
TOUCH_RES_Y = 4096          # Touch resolution in Y direction
DISPLAY_RES_X = 1024        # Display resolution in X direction
DISPLAY_RES_Y = 600         # Display resolution in Y direction

# Environment
env = os.environ.copy()
env[ 'TERM' ] = TERM
env[ 'LANG' ] = 'en_US.UTF-8'

# Initializing
actions = []                # Available menu actions
proc = None                 # Stores the current (sub) process
last_cmd = None             # Last command that was running
tty = ''                    # Active TTY
bl_buffer = bytearray( [ 0, 0, 0, 0 ] * DISPLAY_RES_X * DISPLAY_RES_Y )
ov_buffer = bytearray()     # Overlay buffer data

# Print error message and exit with code
def err( msg: str, e: None | Exception = None, code: int = 1 ) -> None:
    if e is Exception:
        print( f'[ERR] {msg}: {e}' )
    else:
        print( f'[ERR] {msg}' )
    quit( code )

# Determine the active TTY device
# This is used to write output to the correct terminal
def active_tty() -> None:
    global tty
    try:
        with open( '/sys/class/tty/tty0/active', 'r' ) as f:
            active = f.read().strip()
            tty = f'/dev/{active}'
    except Exception as e:
        err( 'Failed to determine active TTY', e )

# Reset terminal to a clean state
def reset_terminal( sleep: float = 0.1 ) -> None:
    global tty
    os.system( 'clear && reset' )
    os.system( f'clear > {tty}' )
    os.system( f'tput reset > {tty}' )
    time.sleep( max( 0.1, sleep ) )

# Compile the menu image to a byte array
# This is used to display the menu on the framebuffer
def load_ov_buffer() -> None:
    global ov_buffer
    img = Image.open( IMAGE ).resize(
        ( DISPLAY_RES_X, DISPLAY_RES_Y )
    ).convert( 'RGB' )
    for r, g, b in img.getdata():
        ov_buffer.extend( [ b, g, r, 0 ] )

# Load actions from configuration file
def load_actions() -> list:
    with open( os.path.join( CFG_PATH, 'actions.json' ) ) as f:
        return json.load( f )

# Find the suitable action by position
def find_action( x: int, y: int ) -> ( dict | None ):
    global actions
    for a in actions:
        if ( a[ 'x1' ] <= x <= a[ 'x2' ] and
             a[ 'y1' ] <= y <= a[ 'y2' ] ):
            return a
    return None

# Get the default command from the actions
def default_action() -> ( dict | None ):
    global actions
    return next( ( a for a in actions if a.get( 'default' ) == True ), None )

# Resolve command (replace %DIR% and %TTY%)
def resolve_command( cmd: str ) -> str:
    global tty
    return cmd.replace( '%DIR%', SRC_PATH ).replace( '%TTY%', tty )

# Terminate current (running) process if there is one
def terminate_proc() -> None:
    global proc
    if proc:
        pid = os.getpgid( proc.pid ) # type: ignore
        try:
            os.killpg( pid, signal.SIGTERM ) # type: ignore
            proc.wait( timeout = 1 )
        except Exception:
            os.killpg( pid, signal.SIGKILL ) # type: ignore
        proc = None

# Run command as sub process
def run_command( cmd: str ) -> None:
    global proc, last_cmd, tty
    try:
        t = open( tty, 'w' )
        proc = subprocess.Popen(
            resolve_command( cmd ),
            shell = True,
            start_new_session = True,
            env = env,
            stdout = t,
            stderr = t,
            stdin = t
        )
        last_cmd = cmd
    except Exception as e:
        err( f'Failed to run command <{cmd}>', e )

# Run the previous command if it exists
def run_last() -> None:
    global last_cmd
    if last_cmd:
        run_command( last_cmd )

# Show overlay using menu image
def show_overlay() -> None:
    global ov_buffer, tty
    try:
        with open( FRAMEBUFFER, 'wb' ) as fb:
            fb.write( ov_buffer )
        os.system( f'tput civis > {tty}' )
    except Exception as e:
        err( 'Failed to show overlay', e )

# Hide / clear the overlay
def hide_overlay() -> None:
    global bl_buffer, tty
    try:
        with open( FRAMEBUFFER, 'wb' ) as fb:
            fb.write( bl_buffer  )
        os.system( f'tput cnorm > {tty}' )
    except Exception as e:
        err( 'Failed to hide overlay', e )

# The main program
def main() -> None:
    global actions
    overlay_vis = touch_active = False
    x = y = None

    # Initialize environment
    active_tty()
    load_ov_buffer()

    # Load available actions
    try:
        actions = load_actions()
        default = default_action()
    except Exception as e:
        err( 'Failed to load actions', e )
        return

    # Grab touch device
    try:
        device = evdev.InputDevice( TOUCH_DEVICE )
        device.grab()
    except Exception as e:
        err( 'Failed to initiate touch device', e )
        return

    # Execute standard command immediately on startup
    if default and default.get( 'cmd' ):
        run_command( default[ 'cmd' ] )
    else:
        show_overlay()
        overlay_vis = True

    # Main loop
    for e in device.read_loop():

        # If the event is a key event, calculate the touch
        # coordinates based on the event type and code
        if e.type == evdev.ecodes.EV_ABS:
            if e.code == evdev.ecodes.ABS_X:
                x = e.value * DISPLAY_RES_X / TOUCH_RES_X
            elif e.code == evdev.ecodes.ABS_Y:
                y = e.value * DISPLAY_RES_Y / TOUCH_RES_Y

        # If the touch coordinates are available, check
        # for actions and run the corresponding command
        # if an action is found
        elif ( e.type == evdev.ecodes.EV_KEY and
               e.code == evdev.ecodes.BTN_TOUCH ):
            if e.value == 1:
                touch_active = True
            elif e.value == 0 and touch_active:
                touch_active = False
                if x is not None and y is not None:
                    if not overlay_vis:
                        terminate_proc()
                        reset_terminal()
                        show_overlay()
                        overlay_vis = True
                    else:
                        action = find_action( x, y )
                        if action and action.get( 'cmd' ):
                            terminate_proc()
                            hide_overlay()
                            overlay_vis = False
                            reset_terminal( 0.5 )
                            run_command( action[ 'cmd' ] )
                            if action.get( 'rerun' ):
                                terminate_proc()
                                reset_terminal( 0.5 )
                                run_last()

# Run the program
# Safely execute the main function
if __name__ == '__main__':
    main()

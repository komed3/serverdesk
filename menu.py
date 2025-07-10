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

# Display
TOUCH_DEVICE = '/dev/input/event3'
FRAMEBUFFER = '/dev/fb0'
TOUCH_RES_X = 4096      # Touch resolution in X direction
TOUCH_RES_Y = 4096      # Touch resolution in Y direction
DISPLAY_RES_X = 1024    # Display resolution in X direction
DISPLAY_RES_Y = 600     # Display resolution in Y direction

# Constants
MENU_IMAGE = os.path.join( IMG_PATH, 'menu.png' )

# Initializing
actions = []            # Available menu actions
proc = None             # Stores the current (sub) process
overlay_vis = False     # If the overlay is visible
last_cmd = None         # Last command that was running

# Load actions from configuration file
def load_actions() -> list:
    with open( os.path.join( CFG_PATH, 'actions.json' ) ) as f:
        return json.load( f )

# Find the suitable action by position
def find_action( x: int, y: int ) -> ( dict | None ):
    for a in actions:
        if ( a[ 'x1' ] <= x <= a[ 'x2' ] and
             a[ 'y1' ] <= y <= a[ 'y2' ] ):
            return a
    return None

# Get the default command from the actions
def default_action() -> ( dict | None ):
    return next(
        ( a for a in actions if a.get( 'default' ) == True ),
        None
    )

# Resolve command (replace %DIR% with source path)
def resolve_command( cmd: str ) -> str:
    return cmd.replace( '%DIR%', SRC_PATH )

# Terminate current running process if there is one
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
    os.system( 'clear' )

# Run command as sub process
def run_command( cmd: str ) -> None:
    global proc, last_cmd
    terminate_proc()
    time.sleep( 0.25 )
    try:
        proc = subprocess.Popen(
            resolve_command( cmd ),
            shell = True,
            start_new_session = True
        )
        last_cmd = cmd
    except Exception as e:
        print( f'[ERR] Failed to run command "{cmd}": {e}' )
        quit( 1 )

# Run the previous command if it exists
def run_last() -> None:
    if last_cmd:
        run_command( last_cmd )

# Show overlay using menu image
def show_overlay() -> None:
    try:
        img = Image.open( MENU_IMAGE ).resize(
            ( DISPLAY_RES_X, DISPLAY_RES_Y )
        ).convert( 'RGB' )
        data = bytearray()
        for r, g, b in img.getdata():
            data.extend( [ b, g, r, 0 ] )
        with open( FRAMEBUFFER, 'wb' ) as fb:
            fb.write( data )
    except Exception as e:
        print( f'[ERR] Failed to show overlay: {e}' )

# Hide / clear the overlay
def hide_overlay() -> None:
    try:
        black = bytearray( [ 0, 0, 0, 0 ] * DISPLAY_RES_X * DISPLAY_RES_Y )
        with open( FRAMEBUFFER, 'wb' ) as fb:
            fb.write( black )
    except Exception as e:
        print( f'[ERR] Failed to hide overlay: {e}' )

# The main program
def main() -> None:
    global actions, overlay_vis
    touch_active = False
    x = y = None

    # Load available actions
    try:
        actions = load_actions()
    except Exception as e:
        print( f'[ERR] Failed to load actions: {e}' )
        return

    # Initiate touch device
    try:
        device = evdev.InputDevice( TOUCH_DEVICE )
        device.grab()
    except Exception as e:
        print( f'[ERR] Failed to initiate touch device: {e}' )
        return

    # Execute standard command immediately on startup
    default = default_action()
    if default and default.get( 'cmd' ):
        run_command( default[ 'cmd' ] )

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
                        show_overlay()
                        overlay_vis = True
                    else:
                        action = find_action( x, y )
                        if action and action.get( 'cmd' ):
                            run_command( action[ 'cmd' ] )
                            if action.get( 'rerun' ):
                                run_last()
                            hide_overlay()
                            overlay_vis = False

# Run the program
# Safely execute the main function
if __name__ == '__main__':
    main()

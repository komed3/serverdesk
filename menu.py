#!/usr/bin/env python3

import evdev # type: ignore
import json
import os
import pygame # type: ignore
import subprocess
import time

# Paths
SRC_PATH = os.path.dirname( os.path.realpath( __file__ ) )
CFG_PATH = os.path.join( SRC_PATH, 'cfg' )
BIN_PATH = os.path.join( SRC_PATH, 'bin' )
IMG_PATH = os.path.join( SRC_PATH, 'assets' )

# Display
TOUCH_DEVICE = '/dev/input/event3'
TOUCH_RES_X = 4096
TOUCH_RES_Y = 4096
DISPLAY_RES_X = 1024
DISPLAY_RES_Y = 600

# Constants
TIMEOUT_SEC = 4

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

# Resolve command (replace %DIR% with source path)
def resolve_command( cmd: str ) -> str:
    return cmd.replace( '%DIR%', SRC_PATH )

# Terminate current running process if there is one
def terminate_proc() -> None:
    global proc
    if proc:
        try:
            proc.terminate()
            proc.wait( timeout = 1 )
        except Exception:
            proc.kill()
        proc = None

# Run command as sub process
def run_command( cmd: str ) -> None:
    global proc, last_cmd
    terminate_proc()
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

# Show overlay with menu image
def show_overlay( screen, img ) -> None:
    screen.blit( img, ( 0, 0 ) )
    pygame.display.flip()

# Clear the overlay by filling the screen with black
def hide_overlay( screen ) -> None:
    screen.fill( ( 0, 0, 0 ) )
    pygame.display.flip()

# The main program
def main() -> None:
    global actions, overlay_vis
    x = y = last_touch = None

    # Load available actions
    try:
        actions = load_actions()
    except Exception as e:
        print( f'[ERR] Failed to load actions: {e}' )
        return

    # Initiate pygame for menu overlay
    try:
        pygame.init()
        pygame.mouse.set_visible( False )
        img = pygame.image.load( os.path.join( IMG_PATH, 'menu.png' ) )
        screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
    except Exception as e:
        print( f'[ERR] Failed to initiate pygame: {e}' )
        return

    # Initiate touch device
    try:
        device = evdev.InputDevice( TOUCH_DEVICE )
        device.grab()
    except Exception as e:
        print( f'[ERR] Failed to initiate touch device: {e}' )
        return
    
    # Execute standard command (htop) immediately on startup
    run_command( 'sudo htop' )

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
               e.code == evdev.ecodes.BTN_TOUCH and
               e.value == 1 ):
            last_touch = time.time()
            if x is not None and y is not None:
                if not overlay_vis:
                    show_overlay( screen, img )
                    overlay_vis = True
                else:
                    action = find_action( x, y )
                    if action and action.get( 'cmd' ):
                        run_command( action[ 'cmd' ] )
                        if action.get( 'rerun' ):
                            run_last()
                        hide_overlay( screen )
                        overlay_vis = False

        # If the overlay is visible and the last touch
        # was more than TIMEOUT_SEC ago, hide the overlay
        # and reset last_touch
        elif ( overlay_vis and last_touch and
               time.time() - last_touch > TIMEOUT_SEC ):
            hide_overlay( screen )
            overlay_vis = False
            last_touch = None

# Run the program
# Safely execute the main function
if __name__ == '__main__':
    main()

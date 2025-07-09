#!/usr/bin/env python3

import evdev # type: ignore
import json
import os
import pygame # type: ignore
import subprocess
import time

# Paths & constants
SRC_PATH = os.path.dirname( os.path.realpath( __file__ ) )
CFG_PATH = os.path.join( SRC_PATH, 'cfg' )
BIN_PATH = os.path.join( SRC_PATH, 'bin' )
IMG_PATH = os.path.join( SRC_PATH, 'assets' )

TOUCH_DEVICE = '/dev/input/event3'
TIMEOUT_SEC = 4

# Initializing
actions = []            # Available menu actions
proc = None             # Stores the current (sub) process
overlay_vis = False     # If the overlay is visible
last_cmd = None         # Last command that was running

# Load actions from configuration file
def load_actions():
    with open( os.path.join( CFG_PATH, 'actions.json' ) ) as f:
        return json.load( f )

# Find the suitable action by position
def find_action( x: int, y: int ) -> ( str | None ):
    for a in actions:
        if ( a[ 'x1' ] <= x <= a[ 'x2' ] and
             a[ 'y1' ] <= y <= a[ 'y2' ] ):
            return a[ 'cmd' ]
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

# The main program
def main() -> None:
    global actions
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
        screen.blit( img, ( 0, 0 ) )
        pygame.display.flip()
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

    # Main loop
    for e in device.read_loop():
        if e.type == evdev.ecodes.EV_ABS:
            if e.code == evdev.ecodes.ABS_X:
                x = e.value * 1024 / 4096
            elif e.code == evdev.ecodes.ABS_Y:
                y = e.value *  600 / 4096
        elif ( e.type == evdev.ecodes.EV_KEY and
               e.code == evdev.ecodes.BTN_TOUCH and
               e.value == 1 ):
            if x is not None and y is not None:
                action = find_action( x, y )
                if action:
                    run_command( action )
                last_touch = time.time()
        elif last_touch and ( time.time() - last_touch > TIMEOUT_SEC ):
            screen.blit( img, ( 0, 0 ) )
            pygame.display.flip()
            last_touch = None

# Run the program
main()

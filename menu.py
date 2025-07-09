#!/usr/bin/env python3

import json
import os
import subprocess

# Paths
SRC_PATH = os.path.dirname( os.path.realpath( __file__ ) )
CFG_PATH = os.path.join( SRC_PATH, 'cfg' )
BIN_PATH = os.path.join( SRC_PATH, 'bin' )

# Available menu actions
actions = []

# Stores the current (sub) process
proc = None

# Load actions from configuration file
def load_actions():
    with open( os.path.join( CFG_PATH, 'actions.json' ) ) as f:
        return json.load( f )

# Resolve command (replace %DIR% with source path)
def resolve_command( cmd: str ):
    return cmd.replace( '%DIR%', SRC_PATH )

# Terminate current running process if there is one
def terminate_proc():
    global proc
    if proc:
        try:
            proc.terminate()
            proc.wait( timeout = 1 )
        except Exception:
            proc.kill()
        proc = None

# Run command as sub process
def run_command( cmd: str ):
    global proc
    terminate_proc()
    proc = subprocess.Popen(
        cmd, shell = True,
        start_new_session = True
    )

# Find the suitable action by position
def find_action( x: int, y: int ):
    for a in actions:
        if ( a[ 'x1' ] <= x <= a[ 'x2' ] and
             a[ 'y1' ] <= y <= a[ 'y2' ] ):
            return a
    return None

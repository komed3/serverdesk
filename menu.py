#!/usr/bin/env python3

import os
import subprocess

# Available menu actions
actions = None

# Stores the current (sub) process
proc = None

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
def run_command( cmd ):
    global proc
    terminate_proc()
    proc = subprocess.Popen(
        cmd, shell = True,
        preexec_fn = os.setsid
    )

# Find the suitable action by position
def find_action( x, y ):
    for a in actions:
        if a[ 'x1' ] <= x <= a[ 'x2' ] and a[ 'y1' ] <= y <= a[ 'y2' ]:
            return a
    return None

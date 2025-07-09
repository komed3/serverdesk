#!/usr/bin/env python3

import os
import subprocess

proc = None

# Terminate current running process if there is one
def terminate_proc ():
    global proc
    if proc:
        try:
            proc.terminate()
            proc.wait( timeout = 1 )
        except Exception:
            proc.kill()
        proc = None

# Run command as sub process
def run_command ( cmd ):
    global proc
    terminate_proc()
    proc = subprocess.Popen(
        cmd, shell = True,
        preexec_fn = os.setsid
    )

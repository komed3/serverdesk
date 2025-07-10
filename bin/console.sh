#!/bin/bash

# Define shell target
if [[ "$1" == "--admin" ]]; then
    USER="admin"
    TARGET_TTY=7
    SHELL_CMD="sudo -u $USER bash -l"
elif [[ "$1" == "--root" ]]; then
    USER="root"
    TARGET_TTY=8
    SHELL_CMD="bash -l"
else
    echo "Usage: $0 --admin | --root"
    exit 1
fi

# Determine current console
CURRENT_TTY=$( fgconsole )

# Start shell (only if not already active)
if ! ps -t tty$TARGET_TTY | grep -q bash; then
    sudo openvt -c "$TARGET_TTY" -- $SHELL_CMD
fi

# Switch to the target console
sudo chvt "$TARGET_TTY"

# Wait until user changes back
while true; do
    ACTIVE_TTY=$( fgconsole )
    if [[ "$ACTIVE_TTY" == "$CURRENT_TTY" ]]; then
        break
    fi
    sleep 1
done

# Return to the original console
# Just to be on the safe side
sudo chvt "$CURRENT_TTY"
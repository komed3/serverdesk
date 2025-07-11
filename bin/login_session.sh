#!/bin/bash

TTYNUM=3
TTYDEV="/dev/tty$TTYNUM"
TTYONE="/dev/tty1"

# Switch to login TTY
sudo chvt "$TTYNUM"
sleep 0.2

# Keep loop open as long as login has not been successfully completed
sudo setsid bash -c "
  exec < $TTYDEV > $TTYDEV 2>&1
  while true; do
    login
    sleep 1
  done
"

# After logout: switch back to the ServerDesk console
sudo chvt "${SERVERDESK_TTY#/dev/tty}"

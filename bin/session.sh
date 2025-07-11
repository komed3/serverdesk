#!/bin/bash

# Switch to login TTY
sudo chvt 3
sleep 0.2

# Keep loop open as long as login has not been successfully completed
sudo setsid bash -c "
  exec < /dev/tty3 > /dev/tty3 2>&1
  while true; do
    login
    sleep 1
  done
"

# After logout: switch back to the ServerDesk console
sudo chvt 1

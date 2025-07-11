#!/bin/bash

# Switch to login TTY
chvt 3

# Wait briefly for a clean switchover
sleep 0.2

# Start login (blocking)
exec </dev/tty3 > /dev/tty3 2>&1
setsid login
RET=$?

# After logout: switch back to the ServerDesk console
chvt 1

# Show errors
exit $RET

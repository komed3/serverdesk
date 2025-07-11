#!/bin/bash

# Interrupt ServerDesk
sudo systemctl stop serverdesk.service

# Switch to TTY3
sudo chvt 3

# Wait until a user logs out
#while who | grep -q 'tty3'; do
#    sleep 1
#done

# Switch back to TTY1
#sudo chvt 1

# Restart ServerDesk
#sudo systemctl restart serverdesk.service

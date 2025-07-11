#!/bin/bash

# Interrupt ServerDesk
sudo systemctl stop serverdesk.service
clear

# Login shell on the same console
exec /bin/login

# Wait until a user logs out
while who | grep -q 'tty1'; do
    sleep 1
done

# Restart ServerDesk
sudo systemctl restart serverdesk.service

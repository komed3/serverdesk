#!/bin/bash

# Switch to TTY3
sudo chvt 3

# Interrupt ServerDesk
sudo systemctl stop serverdesk.service

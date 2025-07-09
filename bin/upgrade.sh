#!/usr/bin/env bash

# Check sudo rights
[ "$( id -u )" -ne 0 ] && echo "[ERR] This script requires root rights." && exit 1

# Colors
RESET='\033[0m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'

# Helper function to display a countdown before proceeding
countdown () {
    local seconds=$1
    for i in $( seq "$seconds" -1 1 ); do
        echo -ne "${CYAN}... proceed in $i sec ...\r${RESET}"
        sleep 1
    done
    echo ""
}

# Step 1 – Update package sources
echo -e "${GREEN}=== Step 1: Update package sources ===${RESET}"
apt update

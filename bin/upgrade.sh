#!/bin/bash

# Colors
RESET='\033[0m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'

# Helper function to display a countdown before proceeding
countdown () {
    local seconds=$1
    if (( seconds > 0 )); then
        echo
        for i in $( seq "$seconds" -1 1 ); do
            echo -ne "${CYAN}... proceed in $i sec ...\r${RESET}"
            sleep 1
        done
    fi
    echo
}

# Begin
echo -e "${YELLOW}[Check for available package updates]${RESET}"

countdown 0

# Step 1 – Update package sources
echo -e "${YELLOW}[Step 1/6] Update package sources${RESET}"
sudo apt update

countdown 0

# Step 2 - Show list of upgradable packages
echo -e "${YELLOW}[Step 2/6] Packages that need to be updated${RESET}"
sudo apt list --upgradable 2>/dev/null | tail -n +2

# Wait for some time depending on the number of packages to be updated
updates_count=$( apt list --upgradable 2>/dev/null | wc -l )
wait_time=$(( updates_count < 2 ? 3 : ( updates_count > 10 ? 10 : updates_count ) ))
countdown $wait_time

# Step 3 – Upgrade
echo -e "${YELLOW}[Step 3/6] Upgrade installed packages${RESET}"
sudo apt upgrade -y

countdown 0

# Step 4 – Distribution upgrade
echo -e "${YELLOW}[Step 4/6] System upgrade (distribution)${RESET}"
sudo apt dist-upgrade -y

countdown 5

# Step 5 – Autoremove not used packages
echo -e "${YELLOW}[Step 5/6] Remove packages no longer needed${RESET}"
sudo apt autoremove -y

countdown 0

# Step 6 – Clean up package cache
echo -e "${YELLOW}[Step 6/6] Clean up package cache${RESET}"
sudo apt clean

countdown 0

# Finishing
echo -e "${YELLOW}[System has been successfully upgraded]${RESET}"

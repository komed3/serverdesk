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

    echo

    if (( seconds > 0 )); then
        for i in $( seq "$seconds" -1 1 ); do
            echo -ne "${CYAN}... proceed in $i sec ...\r${RESET}"
            sleep 1
        done
    fi

    echo

}

# Step 1 – Update package sources
echo -e "${GREEN}=== Step 1: Update package sources ===${RESET}"
apt update

countdown 0

# Step 2 - Show list of upgradable packages
echo -e "${GREEN}=== Step 2: Packages that need to be updated ===${RESET}"
apt list --upgradable 2>/dev/null | tail -n +2

# Wait for some time depending on the number of packages to be updated
updates_count=$( apt list --upgradable 2>/dev/null | wc -l )
wait_time=$(( updates_count < 2 ? 3 : ( updates_count > 10 ? 10 : updates_count ) ))
countdown $wait_time

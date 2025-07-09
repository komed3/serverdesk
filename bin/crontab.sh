#!/usr/bin/env bash

# Cron files
CRONTAB='/etc/crontab'
CRONDIR='/etc/cron.d'

# Colors
RESET='\033[0m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
TAB=$'\t'

# Helper function to display a header
print_header () {
    echo -e "${CYAN}MI${TAB}H${TAB}D${TAB}M${TAB}W${TAB}USER${TAB}CMD${RESET}"
}

# Helper function to clean up cron lines
# This function removes comments, empty lines, and leading spaces
clean_cron_lines () {
    while read -r line; do
        echo "${line}" |
            grep -vE '^($|\s*#|\s*[[:alnum:]_]+=)' |
            sed -E 's/\s+/ /g' |
            sed -E 's/^ //'
    done
}

# Helper function to look up run-parts in cron files
# This function expands run-parts commands to list individual scripts
# It reads from standard input and outputs the expanded cron jobs
lookup_run_parts () {
    while read -r line; do
        match=$( echo "${line}" | grep -oE 'run-parts( +[^ ]+)* +[^ ]+' )
        if [[ -z "${match}" ]]; then
            echo "${line}"
        else
            cron_fields=$( echo "${line}" | cut -d' ' -f1-6 )
            cron_job_dir=$( echo "${match}" | awk '{print $NF}' )
            if [[ -d "${cron_job_dir}" ]]; then
                for cron_job_file in "${cron_job_dir}"/*; do
                    [[ -f "${cron_job_file}" ]] && echo "${cron_fields} ${cron_job_file}"
                done
            fi
        fi
    done
}

# Function to list system cron jobs
# This function reads the system cron files and formats the output
# It displays the cron jobs in a tabular format with headers
list_system_cron () {
    echo -e "\n${YELLOW}[System cron jobs]${RESET}"
    print_header
    {
        [[ -f "$CRONTAB" ]] && cat "$CRONTAB"
        [[ -d "$CRONDIR" ]] && cat "$CRONDIR"/*
    } 2>/dev/null |
        clean_cron_lines |
        lookup_run_parts |
        sed -E "s/^(\S+) (\S+) (\S+) (\S+) (\S+) (\S+) /\1\t\2\t\3\t\4\t\5\t\6\t/" |
        column -s"$TAB" -t
}

# Function to list user cron jobs
# This function reads the user cron jobs from the system and formats the output
# It displays the cron jobs in a tabular format with headers
function list_user_cron () {
    echo -e "\n${YELLOW}[User cron jobs]${RESET}"
    print_header
    while IFS=: read -r user _; do
        crontab -l -u "$user" 2>/dev/null |
            clean_cron_lines |
            sed -E "s/^((\S+ +){5})(.+)$/\1${user} \3/"
    done < /etc/passwd |
        sed -E "s/^(\S+) (\S+) (\S+) (\S+) (\S+) (\S+) /\1\t\2\t\3\t\4\t\5\t\6\t/" |
        column -s"$TAB" -t
}

#!/usr/bin/env bash

# Cron files
CRONTAB='/etc/crontab'
CRONDIR='/etc/cron.d'
ANACRON='/etc/anacrontab'

# Colors
RESET='\033[0m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'

# Helper function to display a header
print_header () {
    echo -e "${CYAN}MI\tH\tD\tM\tW\tUSER\tCMD${RESET}"
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
function lookup_run_parts () {
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

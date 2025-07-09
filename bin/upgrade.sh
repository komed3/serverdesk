#!/usr/bin/env bash

# Check sudo rights
[ "$( id -u )" -ne 0 ] && echo "[ERR] This script requires root rights." && exit 1


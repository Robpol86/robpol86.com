#!/bin/bash
#
# Copyright (c) 2022 Robpol86. All Rights Reserved.
#
# Reboot if there is no internet.
#

set -eu

INTERVAL=15m  # Sleep between checks.
PING_TIMEOUT_SECONDS=5  # Abort ping command if it takes too long.
PING_HOSTS=()  # Populate in /etc/default/auto_reboot.

if [ -f /etc/default/auto_reboot ]; then
        . /etc/default/auto_reboot
fi

# Main loop.
while sleep "$INTERVAL"; do
    for ip in "${PING_HOSTS[@]}"; do
        if timeout -t $PING_TIMEOUT_SECONDS ping -c1 $ip; then
            continue 2
        fi
    done
    reboot
done

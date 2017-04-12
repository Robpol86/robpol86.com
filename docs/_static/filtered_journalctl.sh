#!/bin/bash

# Print filtered journalctl entries.
# https://github.com/Robpol86/robpol86.com/blob/master/docs/_static/filtered_journalctl.sh
# Save as (chmod +x): /usr/local/bin/filtered_journalctl

set -e  # Exit script if a command fails.
set -u  # Treat unset variables as errors and exit immediately.
set -o pipefail  # Exit script if pipes fail instead of just the last program.

# Iterate journalctl lines.
journalctl -o json "$@" |while read -r line; do
    comm=
    container_name=
    hostname=
    ident=
    message=
    pid=
    timestamp=

    # Read JSON into bash variables.
    while IFS="=" read -r -d '' key value; do
        case "$key" in
            __REALTIME_TIMESTAMP) timestamp="$value" ;;
            _COMM) comm="$value" ;;
            _HOSTNAME) hostname="$value" ;;
            _PID) pid="$value" ;;
            CONTAINER_NAME) container_name="$value" ;;
            MESSAGE) message="$value" ;;
            SYSLOG_IDENTIFIER) ident="$value" ;;
        esac
    done < <(jq -j 'to_entries|map("\(.key)=\(.value)")|.[]|.+"\u0000"' <<< "$line")

    # Filter influxdb statements.
    if [ "$container_name" == "influxdb" ] && [ "${message::3}" == "[I]" ]; then
        continue
    fi

    # Handle source column.
    if [ -z "$comm" ]; then
        source="$ident"
    else
        source="$comm[$pid]"
    fi

    # Print.
    echo "$(date -d @${timestamp::-6} '+%b %d %T') $hostname $source: $message"
done

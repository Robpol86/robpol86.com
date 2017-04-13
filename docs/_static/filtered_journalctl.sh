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
    systemd_unit=
    timestamp=
    unit=

    # Read JSON into bash variables.
    while IFS="=" read -r -d '' key value; do
        case "$key" in
            __REALTIME_TIMESTAMP) timestamp="$value" ;;
            _COMM) comm="$value" ;;
            _HOSTNAME) hostname="$value" ;;
            _PID) pid="$value" ;;
            _SYSTEMD_UNIT) systemd_unit="$value" ;;
            CONTAINER_NAME) container_name="$value" ;;
            MESSAGE) message="$value" ;;
            SYSLOG_IDENTIFIER) ident="$value" ;;
            UNIT) unit="$value" ;;
        esac
    done < <(jq -j 'to_entries|map("\(.key)=\(.value)")|.[]|.+"\u0000"' <<< "$line")

    # Filter influxdb statements.
    if [ "$container_name" == "influxdb" ] && [ "${message::3}" == "[I]" ]; then
        continue
    fi

    # Filter intermittent makecache errors.
    if [ "$unit" == "dnf-makecache.service" ]; then
        continue
    fi

    # Filter iptables warnings due to docker.
    if [ "$systemd_unit" == "firewalld.service" ] && [ "${message::24}" == "WARNING: COMMAND_FAILED:" ]; then
        if [[ "${message^^}" == *"DOCKER"* ]] || [[ "$message" == *" br-"* ]]; then continue; fi
        if [[ "${message^^}" =~ $(echo '\b172.1(7|8).0.2\b') ]]; then continue; fi
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

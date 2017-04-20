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
    message=
    pid=
    syslog_ident=
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
            SYSLOG_IDENTIFIER) syslog_ident="$value" ;;
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

    # Filter warnings due to docker.
    if [ "$systemd_unit" == "firewalld.service" ] && [ "${message::24}" == "WARNING: COMMAND_FAILED:" ]; then
        if [[ "${message^^}" == *"DOCKER"* ]] || [[ "$message" == *" br-"* ]]; then continue; fi
        if [[ "${message^^}" =~ $(echo "\b172.1(7|8).0.2\b") ]]; then continue; fi
    elif [ "$syslog_ident" == "systemd-udevd" ]; then
        if [ "${message::50}" == "Could not generate persistent MAC address for veth" ]; then continue; fi
    fi

    # Filter kernel messages.
    if [ "$syslog_ident" == "kernel" ]; then
        if [[ "$message" =~ "audit_printk_skb: "[0-9]+" callbacks suppressed" ]]; then continue; fi
    fi

    # Handle source column.
    if [ -z "$comm" ]; then
        source="$syslog_ident"
    else
        source="$comm[$pid]"
    fi

    # Print.
    echo "$(date -d @${timestamp::-6} '+%b %d %T') $hostname $source: $message"
done

#!/bin/bash
#
# Copyright (c) 2021 Robpol86. All Rights Reserved.
#
# Disables hostapd while home SSID is present in a WiFi access point scan.
#

set -eu

CONFIRM_GONE_ITER=2  # Verify home SSID is missing from scan these many times.
HOME_SSID="FBI SURVEILLANCE VAN"  # Your home WiFi SSID.
INTERVAL=1m  # Sleep between scans.
START_GRACE_PERIOD=5m  # Sleep at the start of this script.

if [ -f /etc/default/wifi_toggle ]; then
        . /etc/default/wifi_toggle
fi

# Scan and search for SSID.
is_home_visible() {
    iw dev wlan0 scan |sed -n 's/^\s\+SSID: //p' |grep -qxF "$HOME_SSID"
}

# Grace period on start.
sleep "$START_GRACE_PERIOD"

# Main loop.
count=0
while true; do
    if is_home_visible; then
        hostapd_cli -iwlan0 disable
        count=0
    elif (( count >= CONFIRM_GONE_ITER )); then
        hostapd_cli -iwlan0 enable
        count=0
    else
        : $((count++))
    fi

    sleep "$INTERVAL"
done

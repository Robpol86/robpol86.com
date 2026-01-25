#!/bin/bash
#
# Copyright (c) 2021 Robpol86. All Rights Reserved.
#
# Starts the wifi_toggle daemon
#

### BEGIN INIT INFO
# Provides:          wifi_toggle
# Required-Start:    $local_fs $networking
# Required-Stop:     $local_fs
# Default-Start:     3 4 5
# Default-Stop:      0 1 2 6
# Short-Description: Disables hostapd while home SSID is present
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin
PIDFILE=/var/run/wifi_toggle.pid

case "$1" in
    start)
        echo "Starting wifi_toggle... $*"
        start-stop-daemon -S -p "$PIDFILE" -m -b -a /bin/bash -- /usr/bin/wifi_toggle.sh
        echo "done"
        ;;
    stop)
        echo -n "Stopping wifi_toggle: "
        start-stop-daemon -K -p "$PIDFILE" && rm "$PIDFILE"
        echo "done"
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    *)
        echo "Usage: start_wifi_toggle { start | stop | restart }" >&2
        exit 1
        ;;
esac

exit 0

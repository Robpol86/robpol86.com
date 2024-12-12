#!/bin/bash
#
# Copyright (c) 2022 Robpol86. All Rights Reserved.
#
# Reboot if there is no internet
#

### BEGIN INIT INFO
# Provides:          auto_reboot
# Required-Start:    $local_fs $networking
# Required-Stop:     $local_fs
# Default-Start:     3 4 5
# Default-Stop:      0 1 2 6
# Short-Description: Reboot if there is no internet
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin
PIDFILE=/var/run/auto_reboot.pid

case "$1" in
    start)
        echo "Starting auto_reboot... $*"
        start-stop-daemon -S -p "$PIDFILE" -m -b -a /bin/bash -- /usr/bin/auto_reboot.sh
        echo "done"
        ;;
    stop)
        echo -n "Stopping auto_reboot: "
        start-stop-daemon -K -p "$PIDFILE" && rm "$PIDFILE"
        echo "done"
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    *)
        echo "Usage: start_auto_reboot { start | stop | restart }" >&2
        exit 1
        ;;
esac

exit 0

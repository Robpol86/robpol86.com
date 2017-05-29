#!/bin/bash

echo "UPS $2 initiated Shutdown Sequence" |wall
/usr/sbin/shutdown -P now "apcupsd UPS ${2} initiated shutdown"
exit 99

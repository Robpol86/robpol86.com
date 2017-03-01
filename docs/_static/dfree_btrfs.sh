#!/bin/bash

# Show Btrfs estimated free space.
#
# https://github.com/Robpol86/robpol86.com/blob/master/docs/_static/dfree_btrfs.sh
#
# Samba by default uses "df" to get free space of a volume. However with Btrfs
# that value isn't what the user may expect. Running "btrfs fi usage" instead.
# Save as (chmod +x): /usr/local/bin/dfree_btrfs
#
# Samba usually passed just '.' for $1 and sets $PWD to the volume it's
# requesting.

set -e  # Exit script if a command fails.
set -u  # Treat unset variables as errors and exit immediately.
set -o pipefail  # Exit script if pipes fail instead of just the last program.

# First get total size from df.
total=$(df $1 |tail -1 |awk '{print $2}')

# Then get free (estimated) from btrfs fi usage.
available=$(btrfs fi usage -k $1 2>/dev/null |grep 'Free (estimated)' |awk '{print $3}')
available=${available::-6}  # Trim ".00KiB" from end.

# Print.
echo "$total $available"

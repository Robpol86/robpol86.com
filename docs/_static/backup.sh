#!/bin/bash

# Create snapshots for Btrfs subvolumes and back them up with rsync.
#
# https://github.com/Robpol86/robpol86.com/blob/master/docs/_static/backup.sh
# Save as (chmod +x): /usr/local/bin/backup

set -e  # Exit script if a command fails.
set -u  # Treat unset variables as errors and exit immediately.
set -o pipefail  # Exit script if pipes fail instead of just the last program.

PREFIX_SOURCE=/storage
PREFIX_TARGET=/backup
LOG_FILE="$PREFIX_TARGET/backup.log"

# Print error to stderr and exit 1.
error () {
    echo -e "\033[31m=> ERROR: $@\033[0m" >&2
    exit 1
}

# Print warning to stderr.
warning () {
    echo -e "\033[33m=> WARNING: $@\033[0m" >&2
}

# Print normal messages to stdout.
print () {
    echo -e "\033[36m=> $(date -u -d @$SECONDS +%T) $@\033[0m"
}

# Handle no arguments specified.
if [[ $# -eq 0 ]]; then
    echo usage: $0 subvolume_name ... >&2
    exit 1
fi

# Verify subvolume exists.
for subvol in $@; do
    [ -d "$PREFIX_SOURCE/$subvol" ] || error "Subvolume $subvol doesn't exist."
    btrfs subvolume list "$PREFIX_SOURCE" |grep -q "path $subvol$" \
        || error ${subvol} is not a subvolume.
done

# Verify target is writable and enable logging to file.
touch "$LOG_FILE" || error Target ${PREFIX_TARGET} is not writable.
exec &> >(tee -ai "$LOG_FILE")
print Started on $(date)

# Main backup function.
do_backup () {
    source="$PREFIX_SOURCE/$1"
    snapshot="$PREFIX_SOURCE/Backup_$1"
    target="$PREFIX_TARGET/$1"
    if [ -d "$snapshot" ]; then
        warning Snapshot ${snapshot} already exists. Removing.
        btrfs subvolume delete "$snapshot"
    fi
    # Create snapshot.
    btrfs subvolume snapshot -r "$source" "$snapshot"
    # Backup.
    rsync -aiv --delete --exclude /Temporary "$snapshot/" "$target"
    # Delete snapshot.
    btrfs subvolume delete "$snapshot"
}

# Run.
for subvol in $@; do
    print Backing up "$subvol"
    do_backup "$subvol"
done

# Scrub every 6 months.
prev_scrub=$(tac "$LOG_FILE" |grep -Pom1 "(?<=^.{5}=> .{8} Scrubbing $PREFIX_TARGET on )\d{10}" || echo 0)
if [ $(( $(date +%s) - prev_scrub )) -gt 15778463 ]; then
    print Scrubbing "$PREFIX_TARGET" on $(date +%s)
    btrfs scrub start -Bd "$PREFIX_TARGET"
fi

# Done.
df -h "$PREFIX_TARGET"
print Done

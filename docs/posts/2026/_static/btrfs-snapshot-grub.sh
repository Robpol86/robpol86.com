#!/bin/sh
set -e

#
# TODO.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/btrfs-snapshot-grub.sh
# Save as (chmod +x): /etc/grub.d/09_bsnaps
# Install in initramfs with: update-grub
#

ten_linux="${0%/*}/10_linux"
[ -x "$ten_linux" ] || exit 1  # Abort if missing/not executable. TODO error message.

# Duplicate 10_linux with edits as new Grub entry.
"$SHELL" "$ten_linux" |awk '
  /^menuentry / {
    in_entry = 1
    sub(/\047$/, " (default subvolume)\047", $2)
  }

  /rootflags=subvol=/ && in_entry {
    before = $0
    sub(/rootflags=subvol=[^ ]+/, "rootflags=")  # TODO space in subvol path?
    after = $0
    modified = before != after
  }

  {
    print
  }

  /^}$/ && in_entry {
    exit
  }

  END {
    if (!modified) exit 1
  }
'

# TODO:
#   - Rename to x_remove_subvol.sh in comment
#   - What if this is installed without restoring snapshots? What's the default set-default?
#   - Confirm if unmodied update-grub fails and notifies user. stderr?
#   - Warn if get-default != current subvol

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
sh "$ten_linux" |awk '
  /^menuentry / {
    entry = 1
    sub(/\047$/, " (default subvolume)\047", $2)
  }
  {
    print
  }
  entry {
    # gsub()  # subvol=.bsnaps/restored/third-1839d999-76ca-49cc-a832-e469e35f8ecb
    effective=1  # TODO only if subvol was stripped.
  }
  /^}$/ {
    if (entry) exit
  }
  END {
    if (!effective) exit 1
  }
'

# TODO:
#   - Rename to x_remove_subvol.sh in comment
#   - What if this is installed without restoring snapshots? What's the default set-default?
#   - Confirm if ineffective update-grub fails and notifies user. stderr?

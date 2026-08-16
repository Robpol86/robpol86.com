#!/bin/sh
set -e

#
# TODO.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/btrfs-snapshot-grub.sh
# Save as (chmod +x): /etc/grub.d/09_bsnaps
# Install in initramfs with: update-grub
#

ten_linux="${0%/*}/10_linux"
[ -x "$ten_linux" ] || exit 0  # Abort if missing/not executable.

# Duplicate 10_linux with edits as new Grub entries.
sh "$ten_linux" |awk '
  {
    print
  }
  /^menuentry / {
    entry=1
    # TODO rename
  }
  entry {
    # gsub()  # subvol=.bsnaps/restored/third-1839d999-76ca-49cc-a832-e469e35f8ecb
  }
  /^}$/ {
    if (entry) exit
  }
'

# TODO:
#   - Rename to x_remove_subvol.sh in comment
#   - What if this is installed without restoring snapshots? What's the default set-default?

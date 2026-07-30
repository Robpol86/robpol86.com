#!/bin/sh -e

# TODO.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/snapshot-restore.sh
# Save as (chmod +x): /usr/lib/dracut/modules.d/82snapshot/snapshot-restore.sh

echo "Hello World Restore"

# TODOs:
# - No no args or bad name list available snapshots
#   - To save typing in rd.break maybe prefix each snapshot with a number and let user specify snapshot-restore -1
# - Test take+restore multiple times, creating complex nesting.
# - Restore: mv nfo to .restored.17234567899
#   - If user makes a new snapshot from a restored one we don’t want a collision.

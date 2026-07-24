#!/bin/bash

#
# Copy snapshot-take and snapshot-restore into initramfs image.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/snapshot-module-setup.sh
# Save as (chmod +x): /usr/lib/dracut/modules.d/82snapshot/module-setup.sh
#

check() {
    return 0
}

depends() {
    echo btrfs
    return 0
}

install() {
    inst "/sbin/snapshot-take" "/sbin/snapshot-take"
    inst "$moddir/snapshot-restore.sh" "/sbin/snapshot-restore"
}

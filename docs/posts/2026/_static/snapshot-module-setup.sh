#!/bin/bash

#
# Copy snapshot-take into initramfs image.
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
    inst_multiple /usr/bin/awk /usr/bin/cut /usr/bin/sort /usr/bin/wc /usr/bin/xargs

    inst /sbin/snapshot-take /sbin/snapshot-take
    sed -i \
        -e '/^SUBVOLUME_DIR=.*@MODULE-SETUP-REPLACE@/ s|=.*|=/sysroot|' \
        "${initdir:?}/sbin/snapshot-take"
}

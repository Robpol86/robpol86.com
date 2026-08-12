#!/bin/bash

#
# Copy btrfs-snapshot into initramfs image.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/btrfs-snapshot-module-setup.sh
# Save as (chmod +x): /usr/lib/dracut/modules.d/82btrfs-snapshot/module-setup.sh
# Install in initramfs with: update-initramfs -u
#

check() {
    return 0
}

depends() {
    echo btrfs
    return 0
}

install() {
    inst_multiple \
        /usr/bin/awk \
        /usr/bin/base64 \
        /usr/bin/cut \
        /usr/bin/date \
        /usr/bin/rmdir \
        /usr/bin/sort \
        /usr/bin/wc \
        /usr/bin/xargs

    inst /sbin/btrfs-snapshot /sbin/btrfs-snapshot
    sed -i \
        -e '/^SUBVOLUME_DIR=.*@MODULE-SETUP-REPLACE@/ s|=.*|=/sysroot|' \
        "${initdir:?}/sbin/btrfs-snapshot"
    ln -s btrfs-snapshot "${initdir:?}/sbin/bss"

    # TODO remove
    inst /dev/stdin /sbin/bss-test <<-'EOF'
#!/bin/sh
for _ in 1 2 3 4 5 6 7 8 9; do
    lastid="$(bss list |awk 'END{print $1}')";
    name="$(date +%s)";
    bss restore -f "$lastid";
    bss take "$name";
done
EOF
}

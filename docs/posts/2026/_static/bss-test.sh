#!/bin/sh
set -eux
bss take "$(date +%s)-start"
comment=
read -r uuid < /proc/sys/kernel/random/uuid
for _ in 1 2 3 4; do
    comment="$uuid $comment"
done
for n in 1 2 3; do
for i in 1 2 3 4 5 6 7 8 9 A B C D E F G H I J K L M; do
    echo "$n:$i"
    lastid="$(bss list |awk 'END{print $1}')";
    name="$(date +%s)";
    bss restore -f "$lastid";
    bss take -c "$comment" "$name";
done
done
echo DONE
# TODO remove this file.
# sudo install -m0755 ~/btrfs-snapshot.sh /sbin/btrfs-snapshot; sudo install -m0755 ~/btrfs-snapshot-module-setup.sh /usr/lib/dracut/modules.d/82btrfs-snapshot/module-setup.sh; sudo install -m0755 ~/bss-test.sh /usr/lib/dracut/modules.d/82btrfs-snapshot/bss-test.sh
# sudo btrfs subv list / -at |awk '{print length($4)}'
# Fails at 3:D.

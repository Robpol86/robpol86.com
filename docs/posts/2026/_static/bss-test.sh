#!/bin/sh
set -eux
bss take "$(date +%s)-start"
comment=
read -r uuid < /proc/sys/kernel/random/uuid
for _ in 1 2 3 4; do
    comment="$uuid $comment"
done
for i in 1 2 3 4 5 6 7 8 9; do
    echo "$i"
    lastid="$(bss list |awk 'END{print $1}')";
    name="$(date +%s)";
    bss restore -f "$lastid";
    bss take -c "$comment" "$name";
done

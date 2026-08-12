#!/bin/sh
set -eu
bss take "$(date +%s)-start"
for _ in 1 2 3 4 5 6 7 8 9; do
    lastid="$(bss list |awk 'END{print $1}')";
    name="$(date +%s)";
    bss restore -f "$lastid";
    bss take "$name";
done

#!/bin/sh
lastid="$(bss list |awk 'END{print $1}')";
name="$(date +%s)";
bss restore -f "$lastid";
bss take "$name";

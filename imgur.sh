#!/bin/bash

###
# Prints a basic <figure><a href=""><img /></a></figure> outline for imgur
# images to quickly embed in jekyll pages using the So Simple Theme.
# Run without arguments for help.
# 
# MIT License
# Copyright (c) 2013 Robpol86
###

[[ $# -lt 1 || $# -gt 3 ]] && echo "One, two, or three imgur codes required. Ex: $0 kAbGJ C357N zo0d6" 1>&2 && exit 1

# Determine correct <figure> class.
echo -n "<figure"
[ $# == 2 ] && echo -n ' class="half"' || ([ $# == 3 ] && echo -n ' class="third"')
echo ">"

# Iterate through images.
[ $# == 1 ] && size="l" || size="m"
for i in $@; do
    echo "    <!--  -->"
    echo "    <a href=\"http://imgur.com/$i\"><div class=\"annotparent\"><img src=\"http://i.imgur.com/$i$size.jpg\">"
    echo '        <div class="annotation shadow-inverted" style="left:2%;top:2%">0000 Month 0</div>'
    echo "    </div></a>"
done

# The rest.
echo "    <figcaption></figcaption>"
echo "</figure>"

exit 0

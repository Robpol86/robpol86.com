#!/usr/bin/env python3

import os, re, json, pdb, sys
from collections import OrderedDict
from datetime import datetime
from textwrap import dedent
from pprint import pprint
from pathlib import Path
from itertools import zip_longest
from shutil import move

BULLET_POS_MD = 0
BULLET_POS_RST = 4


def process(file_in: str, file_out: str):
    print(file_in)
    is_rst = file_in.endswith(".rst")
    bpos = BULLET_POS_RST if is_rst else BULLET_POS_MD
    in_table = False
    with open(file_in, "r") as handle_src:
        with open(file_out, "w") as handle_tgt:
            while (line := handle_src.readline()):
                # Table start/end.
                if "list-table" in line:
                    in_table = True
                    first_col = True
                    print("  table IN")
                    handle_tgt.write(line)
                    continue
                if in_table:
                    if is_rst and re.match(r'^\w', line):
                        in_table = False
                        print("  table OUTr")
                        if not first_col:
                            handle_tgt.write("      -\n")
                        handle_tgt.write(line)
                        continue
                    elif not is_rst and line == "```\n":
                        in_table = False
                        print("  table OUT")
                        if not first_col:
                            handle_tgt.write("  -\n")
                        handle_tgt.write(line)
                        continue
                # Bullet.
                if in_table and (re.match(r'^    . - \.\.', line) or re.match(r'^. - :::', line)):
                    line_lst = list(line)
                    line_lst[bpos] = "*" if first_col else " "
                    line = ''.join(line_lst)
                    first_col = not first_col
                    print("    col")
                handle_tgt.write(line)
    print()


def main(args=sys.argv[1:]):
    for file_in in args:
        file_out = file_in + ".wrt"
        process(file_in, file_out)
        move(file_out, file_in)


if __name__ == "__main__":
    main()

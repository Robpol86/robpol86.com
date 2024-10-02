#!/usr/bin/env python3

import os, re, json, pdb
from collections import OrderedDict
from datetime import datetime
from textwrap import dedent
from pprint import pprint
from pathlib import Path
from itertools import zip_longest

SOURCE_FILE = Path("docs/vw_alltrack_2019.md")


def gen_heading(date_ymd: str) -> str:
    return dedent(f"""\
        ---
        blogpost: true
        date: {date_ymd}
        author: Robpol86
        location: San Francisco
        category: Projects
        tags: car, alltrack, TODO
        ---
    """)


def parse_date(month_abbrev: str, year_short: str, visited: set) -> datetime:
    month = {"Sept": 9, "Jan": 1, "Feb": 2, "Oct": 10, "Dec": 12, "Aug": 8, "June": 6}[month_abbrev]
    year = int(f"20{year_short}")
    visited_key = f"{month} {year}"
    day = 2 if visited_key in visited else 1
    visited.add(visited_key)
    return datetime.strptime(f"{day} {month} {year}", "%d %m %Y")


def main():
    with open(SOURCE_FILE, "r") as handle:
        out_file_handle = None
        visited = set()
        for line in handle:
            if (section_title := re.match(r'^## (\w+) &#39;(\d+) ([\w -]+)', line)):
                # Build date.
                date = parse_date(section_title[1], section_title[2], visited)
                date_ymd = date.strftime("%Y-%m-%d")
                print(f"{line.rstrip()} {date_ymd}")
                # Build filepath and open.
                out_file_path = Path("docs/posts") / str(date.year) / f"{date_ymd}-alltrack.md"
                if out_file_handle:
                    out_file_handle.close()
                out_file_handle = out_file_path.open("w")
                # Write heading and title.
                out_file_handle.write(gen_heading(date_ymd))
                title = section_title[3]
                out_file_handle.write(f"\n# {title}\n")
                # Next.
                continue
            if out_file_handle:
                if line.startswith("#"):
                    line = line[1:]
                out_file_handle.write(line)


if __name__ == "__main__":
    main()

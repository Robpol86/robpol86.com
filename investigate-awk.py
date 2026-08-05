#!/usr/bin/env python3

"""Test script."""

import os
import subprocess
from pathlib import Path


def run(argv, **kwargs) -> str:
    """Run script."""
    root = Path(__file__).parent
    program = root / "investigate-awk.sh"
    env = dict(os.environ, **kwargs.pop("env", {}))
    output = subprocess.check_output([program] + argv, stderr=subprocess.STDOUT, env=env, **kwargs)  # noqa: S603
    return output.decode("utf8")


def main():
    """Define the main function."""
    output = run([])
    print(output)


if __name__ == "__main__":
    main()

"""Interface for command-line script."""

import argparse
import importlib.metadata
import sys


def main():
    """Main driver."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help="show version")

    opt = parser.parse_args()
    if opt.version:
        print(importlib.metadata.version("mccole"))

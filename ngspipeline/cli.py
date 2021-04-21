#!/usr/bin/env python3

"""Command line interface"""

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 1.0', help="Show program's version number and exit.")
    args = parser.parse_args()

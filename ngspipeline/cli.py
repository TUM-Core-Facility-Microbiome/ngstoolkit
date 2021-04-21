#!/usr/bin/env python3

"""Command line interface"""
from . import __version__, _module_name, test

import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--system-test', action='store_true', help="activate verbose logging")
parser.add_argument('-vvv', '--verbose', action='store_true', help="activate verbose logging")
parser.add_argument('-v', '--version', action='version',
                    version=f'{_module_name} version {__version__}', help="show program's version number and exit")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

logging.debug(f"arguments: {args}")

if args.system_test:
    test.test()

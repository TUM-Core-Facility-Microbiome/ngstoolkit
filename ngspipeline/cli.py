#!/usr/bin/env python3

"""Command line interface"""

from . import __version__, _module_name
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', action='version',
                    version=f'{_module_name} {__version__}', help="Show program's version number and exit.")
args = parser.parse_args()

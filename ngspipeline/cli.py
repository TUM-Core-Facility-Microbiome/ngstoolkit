#!/usr/bin/env python3

"""Command line interface"""
from . import __version__, _module_name
import wsl_distro_build

import argparse
import logging

parser = argparse.ArgumentParser()
distro_ctrl_grp = group = parser.add_mutually_exclusive_group()
distro_ctrl_grp.add_argument('-b', '--build', action='store_true', help="(re-)build the wsl distro using docker")
distro_ctrl_grp.add_argument('-t', '--tar', type=str, help="import distribution from a tar file")
distro_ctrl_grp.add_argument('--export', action='store_true', help="export the distro to a tar file and exit")
parser.add_argument('-vvv', '--verbose', action='store_true', help="activate verbose logging")
parser.add_argument('-v', '--version', action='version',
                    version=f'{_module_name} version {__version__}', help="show program's version number and exit")
args = parser.parse_args()


# configure logging
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)


logging.debug(f"arguments: {args}")


# control the distribution
DISTRO_NAME = "ngstoolkitdist-dev"

if args.build:
    logging.info(f"(Re-)Building the ngstoolkit WSL distribution")
    wsl_distro_build.build_ngstoolkit_wsl_distro(DISTRO_NAME, __version__)
elif args.tar:
    wsl_distro_build.import_from_tar(DISTRO_NAME, args.tar)
elif args.export:
    wsl_distro_build.export(DISTRO_NAME, __version__)
    exit(0)







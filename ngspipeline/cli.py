#!/usr/bin/env python3

"""Command line interface"""
from . import __version__, _module_name
import wsl_distro_build

import argparse
import logging

DISTRO_NAME = "ngstoolkitdist"


def build():
    logging.info(f"(Re-)Building the ngstoolkit WSL distribution")
    wsl_distro_build.build_ngstoolkit_wsl_distro(DISTRO_NAME, __version__)


def import_from_tar(tar: str):
    wsl_distro_build.import_from_tar(DISTRO_NAME, tar)


def export_tar():
    wsl_distro_build.export(DISTRO_NAME, __version__, remove_image=False)


if __name__ == '__main__':
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

    if args.build:
        build()
    elif args.tar:
        import_from_tar(args.tar)
    elif args.export:
        export_tar()
        exit(0)

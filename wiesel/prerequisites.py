"""Utils to check prerequisites.
"""

import os

from . import errors, WSL_EXE, utils


def is_windows() -> bool:
    return os.name == 'nt'


def is_compatible_platform() -> bool:
    return is_windows()


def check_compatible():
    if not is_compatible_platform():
        raise errors.IncompatiblePlatform


def is_wsl_installed():
    if WSL_EXE is None:
        return False

    cmd = [WSL_EXE, '--help']
    print(' '.join(cmd))

    p = utils.Process(cmd, encoding='utf-8')
    p.start().wait()
    return p.is_successful()

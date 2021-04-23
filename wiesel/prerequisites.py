"""Utils to check prerequisites.
"""

import os

from . import errors


def is_windows() -> bool:
    return os.name == 'nt'


def is_compatible_platform() -> bool:
    return is_windows()


def check_compatible():
    if not is_compatible_platform():
        raise errors.IncompatiblePlatform

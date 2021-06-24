import os
import re
from typing import Optional, AnyStr, Iterable

from ngssdk.custom_exceptions import WrongFileType
from ngssdk.filename_manipulations.filename_manipulations import remove_extension

"""Methods to check assumptions about files."""

# Pattern for Illumina Naming Convention.  The specification can be found at https://bit.ly/2WE55Tp
illumina_naming_patten: re.Pattern = re.compile(r'(.*?)_(S[0-9]*)_(L[0-9]*)_(R[12])_001')


def has_illumina_read_naming_scheme(path: str, accepted_extensions: Iterable[str] = ('.fastq', '.fastq.gz')) -> bool:
    """Check if a file has a valid directory according to the Illumina Naming
    Convention.  Only read files (R1, R2), not index files (I1, I2) are accepted.
    The specification can be found at https://bit.ly/2WE55Tp.
    A full directory may be supplied.
    """
    filename_with_extension: str = os.path.basename(path)
    filename: str
    try:
        filename = remove_extension(filename_with_extension, accepted_extensions=accepted_extensions)
    except WrongFileType:
        return False

    match: Optional[re.Match[AnyStr]] = illumina_naming_patten.fullmatch(filename)
    return match is not None

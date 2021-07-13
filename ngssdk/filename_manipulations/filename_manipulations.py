from typing import Iterable, Dict
from ngssdk import custom_exceptions


def remove_extension(basename: str, accepted_extensions: Iterable[str] = ('.fastq', '.fastq.gz')):
    """Remove the extension from a given filename.  An Iterable of allowed
    extensions may be supplied.  If no value is supplied for allowed_extensions
    the function will default to .fastq and .fastq.gz files.
    If the extension is not allowed a WrongFileType Exception is raised.
    """
    extension: str
    for extension in accepted_extensions:
        if basename.endswith(extension):
            return basename[:-len(extension)]
    raise custom_exceptions.WrongFileType

import os
from typing import Callable, Iterable

"""Methods to check assumptions about folders."""


def count_files(directory: str, accepted_extensions: Iterable[str],
                validator: Callable[[str], bool] = lambda x: True) -> int:
    count: int = 0
    node: str
    for node in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, node)):
            file: str = node
            if file_matches(file, accepted_extensions, validator):
                count += 1
    return count


def file_matches(file: str, accepted_extensions: Iterable[str],
                 validator: Callable[[str], bool] = lambda x: True) -> bool:
    for file_extension in accepted_extensions:
        if file.endswith(file_extension):
            if validator(file):
                return True
    return False


def each_file_has_decompressed_version(directory):
    compressed = []
    fastq = []
    for node in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, node)):
            if node.endswith(".fastq.gz"):
                compressed.append(node[:-9])
            elif node.endswith(".fastq"):
                fastq.append(node[:-6])
    compressed.sort()
    fastq.sort()

    if len(compressed) == 0:
        # no compressed files
        return True

    return compressed == fastq

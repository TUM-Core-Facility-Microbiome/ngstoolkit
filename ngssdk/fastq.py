class FastqEntry:
    """The class FastqEntry represents an entry in a fastq file"""

    def __init__(self, id, sequence, quality):
        self.id = id
        self.sequence = sequence
        self.quality = quality

    def subsequence(self, start, stop):
        return self.sequence[start:stop]


def iter_fastq(path):
    with open(path, "r") as handle:
        return iter_fastq_from_handle(handle)


def iter_fastq_from_handle(handle):
    name = ""
    seq = ""
    qual = ""

    i = 0
    for line in handle:
        if i == 0:
            name = line.strip()[1:]
        elif i == 1:
            seq = line.strip()
        elif i == 3:
            qual = line.strip()
            yield FastqEntry(name, seq, qual)
            i = -1
        i += 1

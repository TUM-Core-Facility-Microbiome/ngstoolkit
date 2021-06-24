import unittest

from ngssdk.filename_manipulations.filename_manipulations import *


class Test(unittest.TestCase):
    def test_remove_extension(self):
        basename = remove_extension("SampleName_S1_L001_R1_001.fastq")
        self.assertEqual(basename, "SampleName_S1_L001_R1_001")

        basename = remove_extension("SampleName_S1_L001_R1_001.fastq.gz")
        self.assertEqual(basename, "SampleName_S1_L001_R1_001")

        # allow extension
        basename = remove_extension("SampleName_S1_L001_R1_001.fq",
                                    accepted_extensions=[".fq"])
        self.assertEqual(basename, "SampleName_S1_L001_R1_001")

        # with unknown extension.  raise error
        with self.assertRaises(custom_exceptions.WrongFileType):
            remove_extension("SampleName_S1_L001_R1_001.fq")

        with self.assertRaises(custom_exceptions.WrongFileType):
            remove_extension(
                "SampleName_S1_L001_R1_001.fastq.gz",
                accepted_extensions=[".fasta", ".fastq"])


if __name__ == '__main__':
    unittest.main()

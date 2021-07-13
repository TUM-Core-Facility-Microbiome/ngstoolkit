import unittest

from ngssdk.checks.check_file import has_illumina_read_naming_scheme


class Test(unittest.TestCase):
    def test_has_illumina_naming_scheme(self):
        self.assertTrue(has_illumina_read_naming_scheme("SampleName_S1_L001_R1_001.fastq"))
        self.assertTrue(has_illumina_read_naming_scheme("SampleName_S1_L001_R2_001.fastq"))
        self.assertTrue(has_illumina_read_naming_scheme("SampleName_S1_L001_R1_001.fastq.gz"))

        self.assertTrue(has_illumina_read_naming_scheme("003-RF-003-Is-1129-CT1_S3_L001_R2_001.fastq"))

        # full directory
        self.assertTrue(
            has_illumina_read_naming_scheme(r"Data\Intensities\BaseCalls\SampleName_S1_L001_R1_001.fastq.gz"))

        # index files are not accepted
        self.assertFalse(has_illumina_read_naming_scheme("SampleName_S1_L001_I1_001.fastq.gz"))
        self.assertFalse(has_illumina_read_naming_scheme("SampleName_S1_L001_I2_001.fastq.gz"))

        # wrong scheme is not accepted
        self.assertFalse(has_illumina_read_naming_scheme("SampleName_S1a_L001_I2_001.fastq.gz"))
        self.assertFalse(has_illumina_read_naming_scheme("~/.bashrc"))


if __name__ == '__main__':
    unittest.main()

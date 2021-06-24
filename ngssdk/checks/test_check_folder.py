from unittest import TestCase
from ngssdk.checks.check_folder import *

class Test(TestCase):
    def test_file_matches(self):
        validator = lambda x: x.startswith("a")
        self.assertTrue(file_matches("abc.fastq", accepted_extensions=('.fastq',), validator=validator))
        self.assertFalse(file_matches("abc.fastq", accepted_extensions=('.fq',), validator=validator))
        self.assertFalse(file_matches("bc.fastq", accepted_extensions=('.fastq',), validator=validator))

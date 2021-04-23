from unittest import TestCase

from flexec import select, stream_output


class TestDriver(TestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        cls.driver = select.get_best_driver()

    def test_run_cmd(self):
        cmd = self.driver.run_cmd(['echo', '-ne', r'sometext\nsecond line'])
        self.assertListEqual(list(cmd), [b'sometext\n', b'second line'])

    def test_returncode(self):
        cmd = self.driver.run_cmd(['python3', '-c', 'exit'])
        stream_output(cmd)
        self.assertEqual(123, self.driver.returncode)

    def test_success(self):
        cmd = self.driver.run_cmd(['python3', '-c', 'exit(0)'])
        stream_output(cmd)
        self.assertTrue(self.driver.success)

        cmd = self.driver.run_cmd(['python3', '-c', 'exit(123)'])
        stream_output(cmd)
        self.assertFalse(self.driver.success)

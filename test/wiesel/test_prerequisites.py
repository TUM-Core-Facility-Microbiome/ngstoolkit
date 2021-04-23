from unittest import TestCase

import wiesel.prerequisites


class Test(TestCase):
    def test_is_wsl_installed(self):
        if not wiesel.prerequisites.is_compatible_platform():
            self.assertFalse(wiesel.prerequisites.is_wsl_installed())

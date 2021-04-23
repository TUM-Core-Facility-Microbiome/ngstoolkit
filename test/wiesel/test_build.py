import logging
import os
import random
import string
import tempfile
from unittest import TestCase

import wiesel
from wiesel.wsl_distributions.manager import Dockerfile, DistributionTarFile


class TestDockerfile(TestCase):
    @classmethod
    def get_random_temp_path(cls):
        temp = tempfile.NamedTemporaryFile()
        temp.close()
        return os.path.abspath(temp.name)

    def test_build_tar_file(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="test/wiesel/data/docker/dockerfile_test_archlinux",
            docker_context_path="test/wiesel/data/docker",
            distribution_name="built_with_docker",
            install_location=os.path.dirname(self.get_random_temp_path())
        )

        temp = self.get_random_temp_path()

        tar_file = distro_from_dockerfile.build_tar_file(temp)
        self.assertEqual(tar_file, temp)
        self.assertTrue(os.path.isfile(tar_file))
        self.assertTrue(os.path.isfile(temp))

    def test_build_tar_file_without_given_context(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="test/wiesel/data/docker/dockerfile_test_archlinux",
            docker_context_path=None,
            distribution_name="built_with_docker",
            install_location=os.path.dirname(self.get_random_temp_path())
        )

        temp = self.get_random_temp_path()

        tar_file = distro_from_dockerfile.build_tar_file(temp)
        self.assertEqual(tar_file, temp)
        self.assertTrue(os.path.isfile(tar_file))
        self.assertTrue(os.path.isfile(temp))

    def test_build_tar_file_default_name(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="test/wiesel/data/docker/dockerfile_test_archlinux",
            docker_context_path="test/wiesel/data/docker",
            distribution_name="built_with_docker",
            install_location=os.path.dirname(self.get_random_temp_path())
        )

        tar_file = distro_from_dockerfile.build_tar_file()
        self.assertTrue(os.path.isfile(tar_file))
        print(tar_file)

    def test_build(self):
        if wiesel.prerequisites.is_compatible_platform():  # only run this test on WSL compatible platforms
            random_distro_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(32))

            distro_from_dockerfile = Dockerfile(
                dockerfile_path="test/wiesel/data/docker/dockerfile_test_archlinux",
                docker_context_path="test/wiesel/data/docker",
                distribution_name=random_distro_name,
                install_location=os.path.dirname(self.get_random_temp_path())
            )

            distro = distro_from_dockerfile.build()
            distro.unregister()
        else:
            logging.warning("Skipping incompatible testcase.")

    def test_manual_build_from_dockerfile(self):
        if wiesel.prerequisites.is_compatible_platform():  # only run this test on WSL compatible platforms
            random_distro_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(32))

            distro_from_dockerfile = Dockerfile(
                dockerfile_path="test/wiesel/data/docker/dockerfile_test_archlinux",
                docker_context_path="test/wiesel/data/docker",
                distribution_name=random_distro_name,
                install_location=os.path.dirname(self.get_random_temp_path())
            )

            temp = self.get_random_temp_path()

            tar_file = distro_from_dockerfile.build_tar_file(temp)
            distro_from_tar = DistributionTarFile(
                tar_file=tar_file,
                distribution_name=random_distro_name,
                install_location=os.path.dirname(temp)
            )
            d = distro_from_tar.build()
            d.unregister()
        else:
            logging.warning("Skipping incompatible testcase.")
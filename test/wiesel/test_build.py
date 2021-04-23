import logging
import os
import random
import string
import tempfile
from unittest import TestCase

import wiesel
from wiesel.wsl_distributions.manager import Dockerfile


class TestDockerfile(TestCase):
    def test_build_tar_file(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="data/docker/dockerfile_test_archlinux",
            docker_context_path="data/docker",
            distribution_name="built_with_docker",
            install_location="."
        )
        with tempfile.NamedTemporaryFile() as temp:
            tar_file = distro_from_dockerfile.build_tar_file(temp)
            self.assertEqual(tar_file, temp.name)
            self.assertTrue(os.path.isfile(tar_file))
            self.assertTrue(os.path.isfile(temp.name))

    def test_build_tar_file_without_given_context(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="data/docker/dockerfile_test_archlinux",
            docker_context_path=None,
            distribution_name="built_with_docker",
            install_location="."
        )
        with tempfile.NamedTemporaryFile() as temp:
            tar_file = distro_from_dockerfile.build_tar_file(temp)
            self.assertEqual(tar_file, temp.name)
            self.assertTrue(os.path.isfile(tar_file))
            self.assertTrue(os.path.isfile(temp.name))

    def test_build_tar_file_default_name(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="data/docker/dockerfile_test_archlinux",
            docker_context_path="data/docker",
            distribution_name="built_with_docker",
            install_location="."
        )

        tar_file = distro_from_dockerfile.build_tar_file()
        self.assertTrue(os.path.isfile(tar_file))
        print(tar_file)

    def test_build(self):
        if wiesel.prerequisites.is_compatible_platform():  # only run this test on WSL compatible platforms
            random_distro_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(32))

            distro_from_dockerfile = Dockerfile(
                dockerfile_path="data/docker/dockerfile_test_archlinux",
                docker_context_path="data/docker",
                distribution_name=random_distro_name,
                install_location="."
            )

            distro = distro_from_dockerfile.build()
            distro.unregister()
        else:
            logging.warning("Skipping incompatible testcase.")

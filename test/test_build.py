import os
import tempfile
from unittest import TestCase

from wiesel.wsl_distributions.manager import Dockerfile


class TestDockerfile(TestCase):
    def test_build_tar_file(self):
        distro_from_dockerfile = Dockerfile(
            dockerfile_path="./wsl/docker/Dockerfile",
            docker_context_path="./wsl/docker",
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
            dockerfile_path="./wsl/docker/Dockerfile",
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
            dockerfile_path="./wsl/docker/Dockerfile",
            docker_context_path="./wsl/docker",
            distribution_name="built_with_docker",
            install_location="."
        )

        tar_file = distro_from_dockerfile.build_tar_file()
        self.assertTrue(os.path.isfile(tar_file))
        print(tar_file)

    def test_build(self):
        pass

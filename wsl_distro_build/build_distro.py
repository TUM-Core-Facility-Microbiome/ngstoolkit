import os
import pathlib

from wiesel.wsl_distributions import Dockerfile, DistributionTarFile


def build_ngstoolkit_wsl_distro(distro_name: str, ngstoolkit_version: str):
    """
    Build the ngstoolkit WSL distribution.
    This requires docker.

    :param distro_name: name for distro
    :param ngstoolkit_version: version number that will be saved in /usr/local/bin/wsl_distro_version.txt
    :return:
    """

    distro_from_dockerfile = Dockerfile(
        dockerfile_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "build-context", "Dockerfile"),
        docker_context_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "build-context"),
        distribution_name=distro_name,
        install_location=".",
        version=2,
        build_args={'ngstoolkit_version': ngstoolkit_version}
    )

    distro = distro_from_dockerfile.build(force=True)
    if distro:
        print(f"Successfully registered a WSL distribution named {distro.name!r}.")


def export(distro_name: str, ngstoolkit_version: str):
    distro_from_dockerfile = Dockerfile(
        dockerfile_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "build-context", "Dockerfile"),
        docker_context_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "build-context"),
        distribution_name=distro_name,
        install_location=".",
        version=2,
        build_args={'ngstoolkit_version': ngstoolkit_version}
    )

    distro_from_dockerfile.build_tar_file(f"{distro_name}.tar")


def import_from_tar(distro_name: str, tar_file_path: str):
    distro_from_tar = DistributionTarFile(
        distribution_name=distro_name,
        tar_file=tar_file_path,
        install_location=".",
        version=2
    )

    distro = distro_from_tar.build(force=True)
    if distro:
        print(f"Successfully imported a WSL distribution named {distro.name!r}.")
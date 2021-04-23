import abc
import os
import re
import shutil
import tempfile
from itertools import islice
from typing import List, Optional, Union

from typing.io import IO

from wiesel import utils, errors, WSL_EXE


class Distro(object):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def name(self):
        pass


class RegisteredDistribution(Distro):
    def __init__(self, name: str, version: [int, None] = None, install_location: [str, None] = None):
        self.name = name
        self.version = version

    def __str__(self) -> str:
        return f"RegisteredDistribution{{" \
               f"name={self.name}, " \
               f"version={self.version}" \
               f"}}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def export(self, path: str):
        cmd = [WSL_EXE, "--export", self.name, os.path.abspath(path)]

        p = utils.Process(cmd)
        p.start().wait()

        if not p.is_successful():
            raise errors.WslExportFailed(p.stdout)

    def terminate(self):
        pass

    def unregister(self):
        cmd = [WSL_EXE, "--unregister", self.name]

        p = utils.Process(cmd)
        p.start().wait()

        if not p.is_successful():
            raise errors.WslUnregisterFailed(p.stdout)

    def set_version(self, version: int):
        pass

    def run(self, command: List[str], user: str = None) -> utils.Process:
        cmd = [WSL_EXE, "--distribution", self.name]

        if user:
            cmd.append('--user')
            cmd.append(user)

        cmd.append('--')

        for elem in command:
            cmd.append(elem)

        print(' '.join(cmd))

        p = utils.Process(cmd, encoding='utf-8')
        p.start().wait()

        return p


class WSLManager(object):
    def __init__(self):
        self._machines = {}
        self._default_distro = None

    def _get_machines(self):
        self._machines = {}
        self._default_distro = None

        p = utils.Process([WSL_EXE, "--list", "--verbose"])
        p.start().wait()

        print(p.complete_output)

        if not p.is_successful():
            if str(p.stdout).split('\n')[0] == "Windows Subsystem for Linux has no installed distributions.":
                return
            raise errors.WslCommandFailed()

        stdout = p.stdout

        for output in islice(stdout.iterate(), 1, None):  # skip first line
            line = output.inner[2:].strip()
            split = re.split(r' +', line)
            distro_name = split[0]
            distro_version = int(split[2])

            distro = RegisteredDistribution(distro_name, distro_version)

            self._machines[distro_name] = distro

            if output.inner.startswith('*'):
                self._default_distro = distro

    def get_distro(self, distro_name: str) -> Optional[RegisteredDistribution]:
        distro = None
        machines = self.machines
        for machine_name in machines.keys():
            if machine_name == distro_name:
                distro = machines.get(machine_name)
        return distro

    @property
    def machines(self):
        self._get_machines()
        return self._machines

    @property
    def default_distro(self):
        self._get_machines()
        return self._default_distro


class DistributionDefinition(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, distribution_name: str, install_location: str, version: int = None):
        self.distribution_name: str = distribution_name
        self.install_location: str = os.path.abspath(install_location)
        self.version: Optional[int] = version

    @abc.abstractmethod
    def build(self) -> Optional[RegisteredDistribution]:
        pass


class DistributionTarFile(DistributionDefinition):
    def __init__(self, distribution_name: str, tar_file: str, install_location: str, version: int = None):
        super().__init__(distribution_name, install_location, version)
        self.tar_file = os.path.abspath(tar_file)

    def build(self) -> Optional[RegisteredDistribution]:
        cmd = [WSL_EXE, "--import", self.distribution_name, self.install_location, self.tar_file]
        if self.version:
            cmd.append('--version')
            cmd.append(str(self.version))

        print(' '.join(cmd))

        p = utils.Process(cmd)
        p.start().wait()
        print(p.complete_output)
        print(p.returncode)

        if p.returncode == 4294967295:
            if str(p.stdout) == "A distribution with the supplied name already exists.\n\n":
                raise errors.WslImportFailedDuplicate(p.stdout)
            elif str(p.stdout) == "The supplied install location is already in use.\n\n":
                raise errors.WslImportFailedInstallLocationInUse(p.stdout)

            raise errors.WslImportFailed(p.stdout)

        if not p.is_successful():
            raise errors.WslImportFailed(p.stdout)

        wsl_manager = WSLManager()
        return wsl_manager.get_distro(self.distribution_name)


class Dockerfile(DistributionDefinition):
    """WSL distributions (as tar files) can be build using docker export.
    This allows for automatic builds of WSL distributions starting from a Dockerfile.
    """

    def __init__(self, dockerfile_path: str, docker_context_path: Optional[str],
                 distribution_name: str, install_location: str, version: int = None):
        super().__init__(distribution_name, install_location, version)
        self.dockerfile_path: str = os.path.abspath(dockerfile_path)
        if docker_context_path is not None:
            self.docker_context_path: str = os.path.abspath(docker_context_path)
        else:
            self.docker_context_path = os.path.curdir
        self._FILE_SUFFIX = ".wiesel_build.tar"
        self._temp_file = tempfile.NamedTemporaryFile(suffix=self._FILE_SUFFIX)

    def build_tar_file(self, tar_file: Optional[Union[IO, IO[bytes]]] = None) -> str:
        """
        Create a TAR file that can be imported by WSL.
        :param tar_file: TAR file to write. If None is given, a temporary file is created.
        :return: Absolute path of the created TAR file.
        """

        DOCKER_EXE = shutil.which('docker')

        if tar_file is None:
            tar_file = self._temp_file

        docker_container_name = os.path.basename(tar_file.name).replace(self._FILE_SUFFIX, "")
        docker_image_name = f"wiesel_temp:{docker_container_name}"

        # build docker image
        cmd = [DOCKER_EXE, "build",
               "-t", docker_image_name,
               "-f", str(self.dockerfile_path),
               str(self.docker_context_path)]
        print(' '.join(cmd))

        p = utils.Process(cmd, encoding='utf-8')
        p.start().wait()
        p.check_success()

        # create container from image
        cmd = [DOCKER_EXE, "create",
               "--name", docker_container_name,
               docker_image_name]
        print(' '.join(cmd))

        p = utils.Process(cmd, encoding='utf-8')
        p.start().wait()
        p.check_success()

        # export container to tar tar_file
        cmd = [DOCKER_EXE, "export",
               "--output", tar_file.name,
               docker_container_name]
        print(' '.join(cmd))

        p = utils.Process(cmd, encoding='utf-8')
        p.start().wait()
        p.check_success()

        # cleanup
        cmd = [DOCKER_EXE, "rmi",
               docker_image_name]
        print(' '.join(cmd))

        p = utils.Process(cmd, encoding='utf-8')
        p.start().wait()
        p.check_success()

        return os.path.abspath(tar_file.name)

    def build(self) -> Optional[RegisteredDistribution]:
        tar_file = self.build_tar_file()
        distribution_from_tar = DistributionTarFile(
            self.distribution_name, tar_file, self.install_location, self.version)
        return distribution_from_tar.build()

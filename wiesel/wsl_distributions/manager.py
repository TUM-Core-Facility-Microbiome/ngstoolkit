from typing import List

from wiesel import utils, errors

import abc
from itertools import islice
import os
import re
import shutil

WSL_EXE = shutil.which('wsl')


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


class DistributionDefinition(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build(self) -> RegisteredDistribution:
        pass


class DistributionTarFile(DistributionDefinition):
    def __init__(self, distribution_name: str, tar_file: str, install_location: str, version: int = None):
        self.distribution_name = distribution_name
        self.tar_file = os.path.abspath(tar_file)
        self.install_location = os.path.abspath(install_location)
        self.version = version

    def build(self) -> RegisteredDistribution:
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

    @property
    def machines(self):
        self._get_machines()
        return self._machines

    @property
    def default_distro(self):
        self._get_machines()
        return self._default_distro


manager = WSLManager()
print(manager.machines)

try:
    DistributionTarFile("Debian", "../../../debian.tar", "../../debian").build()
except errors.WslImportFailedDuplicate:
    pass

print("Debian" in manager.machines)

d: RegisteredDistribution = manager.default_distro
process = d.run(['ls', '/mnt/c/Users/Zeno'])

print(process.complete_output)

print(manager.machines)

import abc
import os
from typing import Optional

from wiesel import utils, errors
from wiesel.wsl_distributions import RegisteredDistribution, WSL_EXE, WSLManager


class DistributionDefinition(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build(self) -> Optional[RegisteredDistribution]:
        pass


class DistributionTarFile(DistributionDefinition):
    def __init__(self, distribution_name: str, tar_file: str, install_location: str, version: int = None):
        self.distribution_name = distribution_name
        self.tar_file = os.path.abspath(tar_file)
        self.install_location = os.path.abspath(install_location)
        self.version = version

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

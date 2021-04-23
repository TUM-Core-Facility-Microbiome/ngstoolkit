from wiesel import wsl_distributions
from wiesel import utils
from wiesel import path

import os


class Path(object):
    pass


class WslMountedPath(object):
    def __init__(self, windows_path: str, distribution: wsl_distributions.RegisteredDistribution):
        self._path = os.path.abspath(windows_path)
        print(self._path)
        self._distro = distribution
        self._drive_mapping = self._read_mounts()

    def _read_mounts(self):
        drive_mapping = {}

        mount_process = self._distro.run(['mount'])

        if not mount_process.is_successful():
            raise Exception("Could not execute mount")

        line: utils.CmdOutputLine
        for line in mount_process.complete_output:
            mount = path.linux_mount.LinuxMount(line.inner)
            if mount.fs_vfstype == "9p" and mount.opts.get('aname', False) == "drvfs":
                drive_mapping[mount.fs_spec] = mount.fs_file

        print(drive_mapping)
        return drive_mapping

    def translate(self):
        adjusted_path = self._path
        for mapping in self._drive_mapping.keys():
            if self._path.startswith(mapping):
                adjusted_path = adjusted_path.replace(mapping, self._drive_mapping[mapping] + "/")
                break
        return adjusted_path.replace('\\', '/')

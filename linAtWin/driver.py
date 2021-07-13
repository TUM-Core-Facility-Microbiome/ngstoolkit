#!/usr/bin/env python3
import logging
import re
import subprocess
import sys
from abc import abstractmethod
from typing import List, Iterator


class DriverException(Exception):
    pass


class Driver(object):
    def __init__(self):
        self.process = None

    def setup(self):
        pass

    def self_check(self):
        pass

    @abstractmethod
    def run_cmd(self, cmd: str) -> Iterator[bytes]:
        pass

    @property
    def returncode(self) -> [bool, None]:
        if not self.process:
            return None
        return self.process.returncode

    @property
    def success(self) -> bool:
        return self.returncode == 0


class ClassicShellDriver(Driver):
    def __init__(self):
        super().__init__()
        logging.debug(f'using driver ClassicShellDriver')

    def run_cmd(self, cmd: [str, List[str]]) -> Iterator[bytes]:
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        for line in iter(self.process.stdout.readline, b''):
            yield line

        self.process.wait()


class LinuxShellDriver(ClassicShellDriver):
    def __init__(self):
        super().__init__()
        logging.debug(f'using driver LinuxShellDriver')


class WindowsCmdDriver(ClassicShellDriver):
    def __init__(self):
        super().__init__()
        logging.debug(f'using driver WindowsCmdDriver')


class PowerShellDriver(Driver):
    def __init__(self):
        super().__init__()
        self.cmd_prefix = f'powershell.exe'
        self.shellDriver = WindowsCmdDriver()
        self.shellDriver.self_check()
        logging.debug(f'using driver PowerShellDriver')

    def run_cmd(self, cmd: [str, List[str]]) -> Iterator[bytes]:
        prefixed_cmd = f'{self.cmd_prefix} {cmd}'
        return self.shellDriver.run_cmd(prefixed_cmd)


def remove_x00_from_output(string: bytes) -> str:
    return string.decode('utf-8').replace('\x00', '').rstrip()


class WSLDriver(Driver):
    def __init__(self, distro_name='ngstoolkitdist', wsl_distro_version=2):
        super().__init__()
        self.distro_name = distro_name
        self.wsl_distro_version = wsl_distro_version
        self.cmd_prefix = f'wsl -d {self.distro_name} --'
        self.shellDriver = WindowsCmdDriver()
        self.shellDriver.self_check()
        logging.debug(f'using driver {self.__class__.__name__!r}')

    def self_check(self):
        # check if wsl is installed
        wsl_distro_list_proc: Iterator[bytes] = self.shellDriver.run_cmd("wsl -l")
        wsl_disto_list = list(wsl_distro_list_proc)
        if self.shellDriver.process.returncode != 0:
            logging.error("wsl is not configured correctly. wsl -l returned a non-zero exit code.")
            raise DriverException()
        else:
            logging.debug("wsl list command returned successfully")

        # check if distribution is installed
        true = self.run_cmd('true')
        list(true)

        if self.shellDriver.process.returncode != 0:
            logging.error("wsl distro unknown.")
            raise DriverException()
        else:
            logging.debug("wsl known disto.")

        # check if distribution is running in correct WSL version
        proc_version_cmd = self.run_cmd('cat /proc/version')
        proc_version = ''.join(list(map(_decode_output, proc_version_cmd)))
        mayor_version_match = re.search(r'gcc version (\d+).(\d+).(\d+)', proc_version)
        if mayor_version_match:
            mayor = mayor_version_match.group(1)
            if self.wsl_distro_version == 2:
                if int(mayor) < 8:
                    logging.error("wrong wsl version. not version 2.")
                    raise DriverException()
                else:
                    logging.debug('wsl version 2 found.')
                    logging.debug(proc_version)

    def run_cmd(self, cmd: str) -> Iterator[bytes]:
        prefixed_cmd = f'{self.cmd_prefix} {cmd}'
        return self.shellDriver.run_cmd(prefixed_cmd)

    @property
    def returncode(self) -> [bool, None]:
        if not self.shellDriver.process:
            return None
        return self.shellDriver.process.returncode


def _decode_output(byte_string: bytes) -> str:
    return byte_string.decode('utf-8').rstrip()


def decoded_stream(generator: Iterator[bytes]) -> Iterator[str]:
    for byte_line in generator:
        yield _decode_output(byte_line)


def stream_output(generator: Iterator[bytes]):
    for line in decoded_stream(generator):
        print(line)
    print()


def log_output(generator: Iterator[bytes], loglevel=logging.DEBUG):
    for line in decoded_stream(generator):
        try:
            logging.log(loglevel, line)
        except UnicodeEncodeError:
            pass

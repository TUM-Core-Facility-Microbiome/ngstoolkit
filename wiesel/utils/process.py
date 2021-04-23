import sys
import time
from enum import Enum
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
from typing import List, Optional, TypeVar, Generator, Callable, Iterable

from typing.io import IO

from wiesel import utils

_T = TypeVar('_T')


class Channel(Enum):
    STDOUT = 0
    STDERR = 1


class CmdOutputLine(object):
    def __init__(self, inner: [str, bytes], channel: Channel):
        self.inner = inner
        self.channel = channel

    def __str__(self):
        return f"CmdOutputLine{{inner={repr(self.inner)}, channel={self.channel}}}"

    def format_pretty(self, encoding: str = "utf-8") -> str:
        RED: str = "\033[1;31m"
        RESET: str = "\033[0;0m"

        if self.channel is Channel.STDERR:
            return f"{RED}{self.decode()}{RESET}"
        else:
            return self.decode()

    def decode(self, encoding: str = "utf-8") -> str:
        if isinstance(self.inner, str):
            return self.inner
        return self.inner.decode(encoding)

    def is_stdout(self):
        return self.channel is Channel.STDOUT

    def is_stderr(self):
        return self.channel is Channel.STDERR


class CmdFullOutput(object):
    def __init__(self, lines=None):
        if lines is None:
            lines = []
        self._lines: List[CmdOutputLine] = lines

    def append(self, line: CmdOutputLine):
        self._lines.append(line)

    def iterate(self) -> Generator[CmdOutputLine, None, None]:
        for line in self._lines:
            yield line

    def format_pretty(self, encoding: str = "utf-16-le") -> Generator[str, None, None]:
        for line in self._lines:
            yield line.format_pretty(encoding)

    def __str__(self):
        return ''.join(list(self.format_pretty()))

    def __iter__(self) -> Iterable[CmdOutputLine]:
        return iter(self._lines)

    @property
    def stdout(self):
        stdout = []
        for line in self._lines:
            if line.is_stdout():
                stdout.append(line)
        return CmdFullOutput(stdout)

    @property
    def stderr(self):
        stderr = []
        for line in self._lines:
            if line.is_stderr():
                stderr.append(line)
        return CmdFullOutput(stderr)


class Process(object):
    _ON_POSIX = 'posix' in sys.builtin_module_names

    def __init__(self, cmd: List[str], encoding: Optional[str] = 'utf-16-le', text: bool = True):
        self.cmd = cmd
        self._encoding = encoding
        self._text = text
        self._p: [None, Popen] = None
        self._output_list = utils.DoublyLinkedList()
        self._last_read_list_pointer = None

        self._threads: List[Thread] = []

    def start(self: _T) -> _T:
        self._p = Popen(self.cmd, stdout=PIPE, stderr=PIPE, bufsize=1, close_fds=self._ON_POSIX, text=self._text, encoding=self._encoding)
        self._start_enlist_thread(self._p.stdout, Channel.STDOUT, self._output_list)
        self._start_enlist_thread(self._p.stderr, Channel.STDERR, self._output_list)
        return self

    def is_running(self) -> bool:
        if not self._p:
            return False
        return self.returncode is None

    def wait(self) -> None:
        if not self._p:
            return None
        self._p.wait()

    @property
    def pid(self) -> Optional[int]:
        if not self._p:
            return None
        self._p: Popen
        return self._p.pid

    @property
    def returncode(self) -> Optional[int]:
        if not self._p:
            return None
        self._p: Popen
        self._p.poll()
        return self._p.returncode

    def is_successful(self) -> bool:
        return self.returncode == 0

    def _start_enlist_thread(self, source: Optional[IO[_T]], channel: Channel,
                             target_queue: "Queue[CmdOutputLine]") -> None:
        thread = Thread(target=self._enlist_output, args=(source, channel, target_queue))
        thread.daemon = True  # thread dies with the program
        thread.start()
        self._threads.append(thread)

    def get_line_non_blocking(self) -> Optional[CmdOutputLine]:
        return self._get_line()

    def get_lines(self) -> Generator[CmdOutputLine, None, None]:
        while self.is_running():
            for element in self.get_lines_non_blocking():
                yield element

    def get_lines_non_blocking(self) -> Generator[CmdOutputLine, None, None]:
        return self._get_all_available_lines()

    @property
    def complete_output(self) -> CmdFullOutput:
        return CmdFullOutput(lines=[x.get_value() for x in self._output_list.transverse()])

    @property
    def stdout(self) -> CmdFullOutput:
        return self.complete_output.stdout

    @property
    def stderr(self) -> CmdFullOutput:
        return self.complete_output.stderr

    @classmethod
    def _enlist_output(cls, out: Optional[IO[bytes]], channel: Channel, dll: utils.DoublyLinkedList) -> None:
        line: bytes
        for line in iter(out.readline, ''):
            dll.append(CmdOutputLine(line, channel))
        out.close()

    def _get_line(self) -> Optional[CmdOutputLine]:
        pipebyte: CmdOutputLine
        if self._last_read_list_pointer is None:
            list_head: utils.DoublyLinkedListElement = self._output_list.get_head()
            self._last_read_list_pointer = list_head
            if list_head is None:
                return None
            pipebyte = list_head.get_value()
        else:
            next_element: utils.DoublyLinkedListElement = self._last_read_list_pointer.get_next()
            if next_element is None:
                return None
            self._last_read_list_pointer = next_element
            pipebyte = next_element.get_value()
        decoded_pipebyte: CmdOutputLine
        if self._encoding:
            decoded_pipebyte = CmdOutputLine(pipebyte.decode(encoding=self._encoding), pipebyte.channel)
        else:
            decoded_pipebyte = pipebyte

        return decoded_pipebyte

    def _get_all_available_lines(self) -> Generator[CmdOutputLine, None, None]:
        line: CmdOutputLine = self._get_line()

        while line is not None:
            yield line
            line: CmdOutputLine = self._get_line()


class ProcessPool(object):
    def __init__(self):
        self._tasks: List[Process] = []
        self._threads: List[Thread] = []

    def add_task(self, task: Process):
        self._tasks.append(task)

    # def stream_outputs(self):
    #     for task in self._tasks:
    #         thread = Thread(target=task.start().stream_lines, args=(task.pid,))
    #         thread.start()
    #         self._threads.append(thread)

    def start(self):
        for task in self._tasks:
            thread = Thread(target=task.start().wait)
            thread.start()
            self._threads.append(thread)

    def join(self):
        for thread in self._threads:
            thread.join()


def stream(process: Process, prefix: str, sample_rate: float = 0.5,
           bytefilter: Callable[[bytes], bool] = lambda x: True,
           channelfilter: Callable[[Channel], bool] = lambda x: True):
    while process.is_running():
        for pipebyte in process.get_lines_non_blocking():
            if channelfilter(pipebyte.channel) and bytefilter(pipebyte.inner):
                print(f"{prefix}: {pipebyte.format_pretty(process._encoding)}", end='')

        time.sleep(sample_rate)

    for pipebyte in process.get_lines_non_blocking():
        if channelfilter(pipebyte.channel) and bytefilter(pipebyte.inner):
            print(f"{prefix}: {pipebyte.format_pretty(process._encoding)}", end='')

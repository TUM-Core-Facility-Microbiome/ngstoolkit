import asyncio
import io
import subprocess
import time
import sys


class Process(object):
    def __init__(self, cmd: str):
        self.cmd = cmd
        self._p = None
        self.output = []

    def start(self):
        self._p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            inline = self._p.stdout.readline()
            if not inline:
                break
            self.output.append(inline.decode('utf-8'))

    async def wait(self):
        self._p.wait()


async def main():
    p = Process("/home/zeno/code/work/wiesel/tester.py")
    p.start()

    await p.wait()
    print(p._p.returncode)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    forecast = loop.run_until_complete(main())
    loop.close()

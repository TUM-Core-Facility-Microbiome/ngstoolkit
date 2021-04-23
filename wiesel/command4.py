#!/usr/bin/env python3.5
import asyncio
import locale
import sys
from asyncio.subprocess import PIPE
from contextlib import closing


async def readline_and_kill(*args):
    # start child process
    process = await asyncio.create_subprocess_exec(*args, stdout=PIPE)

    # read line (sequence of bytes ending with b'\n') asynchronously
    async for line in process.stdout:
        print("got line:", line.decode(locale.getpreferredencoding(False)), flush=True)

    process.kill()
    return await process.wait()  # wait for the child process to exit


if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
else:
    loop = asyncio.get_event_loop()

with closing(loop):
    sys.exit(loop.run_until_complete(readline_and_kill("/home/zeno/code/work/wiesel/tester.py")))

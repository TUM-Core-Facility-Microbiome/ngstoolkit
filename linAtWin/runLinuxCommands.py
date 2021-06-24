#!/usr/bin/env python3
from .driver import Driver, WSLDriver, stream_output
import logging

logging.basicConfig(
    level=logging.DEBUG
)

driver: Driver = WSLDriver()

driver.self_check()

with open('prepareVMDeb.txt', 'r') as installfile:
    linebuffr = ''
    for line in installfile:
        if line.lstrip().startswith('#'):
            continue

        if line.rstrip().endswith("\\"):
            linebuffr += line.strip()[:-2] + ' '
            continue
        else:
            linebuffr += line.rstrip()

        if linebuffr == '':
            continue

        print(f'$ {linebuffr}')
        stream_output(driver.run_cmd(linebuffr))
        linebuffr = ''

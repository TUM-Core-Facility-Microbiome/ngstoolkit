from sys import platform

from flexec import Driver, WSLDriver, stream_output, LinuxDriver


def test():
    driver: Driver
    if platform == "linux" or platform == "linux2":
        driver = LinuxDriver()
    elif platform == "win32":
        driver = WSLDriver()
    else:
        raise Exception('Unsupported platform')

    driver.self_check()

    iterator = driver.run_cmd(['ls', '-al'])
    stream_output(iterator)

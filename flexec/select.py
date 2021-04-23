from sys import platform

from flexec import Driver, LinuxDriver, WSLDriver


def get_best_driver():
    driver: Driver
    if platform == "linux" or platform == "linux2":
        driver = LinuxDriver()
    elif platform == "win32":
        driver = WSLDriver()
    else:
        raise Exception('Unsupported platform')

    driver.self_check()
    return driver

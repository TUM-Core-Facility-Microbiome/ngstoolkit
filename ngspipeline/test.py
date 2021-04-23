
from flexec import Driver, WSLDriver, stream_output, LinuxDriver, select


def test():
    driver: Driver = select.get_best_driver()
    iterator = driver.run_cmd(['ls', '-al'])
    stream_output(iterator)

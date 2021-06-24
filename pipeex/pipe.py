import abc
import collections
import logging
from typing import Iterator, Generator, List

import linAtWin


class ExecutionFailed(Exception):
    pass


class PrecheckFailed(ExecutionFailed):
    pass


class PostcheckFailed(ExecutionFailed):
    pass


class SkipRest(Exception):
    pass


class FailSilent(SkipRest):
    """Something failed.
    But we don't have to stop pipe execution.
    Go to next part in pipe."""
    pass


PumpExecResults = collections.namedtuple('PumpExecResults', ['precheck', 'prepare', 'run', 'postcheck'])


class Pump(abc.ABC):
    def __init__(self):
        self._return_code = None
        self.driver: [linAtWin.Driver, None] = None

    def precheck(self):
        pass

    def prepare(self):
        pass

    def run(self):
        pass

    def postcheck(self):
        pass

    def execute(self):
        res_precheck, res_prepare, res_run, res_postcheck = (None, None, None, None)
        try:
            res_precheck = self.precheck()
            res_prepare = self.prepare()
            res_run = self.run()
            res_postcheck = self.postcheck()
        except SkipRest as e:
            logging.warning(e)
            self._return_code = 0
            pass
        except ExecutionFailed as e:
            logging.error(e)
            self._return_code = -1
            raise e

        return PumpExecResults(res_precheck, res_prepare, res_run, res_postcheck)

    @property
    def return_code(self):
        if self.driver is not None:
            self._return_code = self.driver.returncode
        return self._return_code


class Pipeline(object):
    def __init__(self):
        self._pipeline: List[Pump] = []
        self._finished = False

    def add_work(self, pipeline_piece: Pump):
        self._pipeline.append(pipeline_piece)

    def execute(self):
        try:
            for pipebit_return in self:
                logging.debug(f'pipebit_return={pipebit_return}')
                pass
        except ExecutionFailed as e:
            self._return_code = -1
            self._finished = True
            raise e
        return self.return_code

    def execute_iter(self) -> Generator:
        self._finished = False
        pipebit: Pump
        for pipebit in self._pipeline:
            exec_results: PumpExecResults = pipebit.execute()
            returncode = pipebit.return_code
            self._return_code = returncode
            logging.debug(f'{pipebit.__class__.__name__} returncode={returncode}')
            logging.debug(f'{pipebit.__class__.__name__} exec_results={exec_results}')
            yield returncode, exec_results
        logging.debug(f'end of execute_iter')
        self._finished = True

    def __iter__(self) -> Iterator:
        return iter(self.execute_iter())

    @property
    def return_code(self):
        return self._return_code

    @property
    def finished(self):
        return self._finished

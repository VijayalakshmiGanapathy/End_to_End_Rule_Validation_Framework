"""
Timer utilities.
"""

from time import perf_counter


class StepTimer:

    def __init__(self):
        self._start = None

    def start(self):
        self._start = perf_counter()

    def stop(self):
        if self._start is None:
            return 0.0

        return perf_counter() - self._start


class Timer:

    def __init__(self):
        self._start = perf_counter()

    def reset(self):
        self._start = perf_counter()

    @property
    def elapsed(self):
        return perf_counter() - self._start

    @property
    def elapsed_str(self):
        return f"{self.elapsed:.2f}s"
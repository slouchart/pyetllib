# -*- coding:utf-8 -*-

__all__ = [
    'log_timed_statistics',
]


import time
from functools import wraps
import logging


def log_timed_statistics(logger_name=None):
    """Returns a decorator that logs the elapsed time
    of a synchronous function call"""
    def timed_statistics_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            time_elapsed = time.perf_counter() - start_time
            logging.getLogger(logger_name).info(f'time elapsed (seconds) '
                                                f'{round(time_elapsed, 4)}')
            return result

        return wrapper
    return timed_statistics_decorator

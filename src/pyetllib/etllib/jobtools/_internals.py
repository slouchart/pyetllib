import functools
import logging

from ._config import log_levels

"""Mapping of method names to logging levels"""
_dynamic_methods = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'ok': log_levels.OK,
    'fail': log_levels.FAIL,
    'prologue': log_levels.PROLOGUE,
    'epilogue': log_levels.EPILOGUE
}


def _dispatch_dynamic_methods(obj, helper, *args, descriptor=None):
    """Helper to avoid repeating the same pattern when defining
    the reporting methods"""

    for f, level in _dynamic_methods.items():
        if args:
            method = functools.partial(helper, *args, level)
        else:
            method = functools.partial(helper, level)
        if descriptor:
            method = descriptor(method)
        setattr(obj, f, method)


def _init_dynamic_methods(klass):
    """Class decorator to initialize the reporting functions
    as static methods"""
    def dummy():  # pragma: no cover
        ...
    _dispatch_dynamic_methods(klass, dummy, descriptor=staticmethod)
    return klass


class _InternalExceptionWrapper(RuntimeError):
    def __init__(self, exc, job_name, *args):
        assert isinstance(exc, Exception)
        self.exc = exc
        self.job_name = job_name
        super().__init__(*args)

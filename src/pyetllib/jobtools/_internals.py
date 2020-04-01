import functools


from ._config import log_levels


import platform
if platform.system().lower() == 'windows':
    from ctypes import windll, c_int, byref
    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)


"""Mapping of method names to logging levels"""
_dynamic_methods = {
    'error': log_levels.ERROR,
    'warning': log_levels.WARNING,
    'info': log_levels.INFO,
    'debug': log_levels.DEBUG,
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

from abc import abstractmethod
import importlib
import inspect
import logging
import functools
import time
import datetime as dt
import os

from .report import JobReport, get_report
from .exceptions import JobAttributeError
from .exceptions import JobImportError, JobNotCallable
from .exceptions import BadJobRefError, BaseJobException

from ._internals import _init_dynamic_methods, _dispatch_dynamic_methods
from ._internals import _InternalExceptionWrapper


@_init_dynamic_methods
class Job:
    """Defines a job either as a regular functions wrapped with
    a decorator or as a subclass"""
    def __new__(cls, *args, **kwargs):
        _dispatch_dynamic_methods(cls, cls._report_helper_default,
                                  descriptor=staticmethod)
        return super().__new__(cls)

    def __init__(self, name=None, func=None, use_job=False,
                 color_output=True, use_stream=False, logfile=None):
        self.func = func

        if self.func:
            self.name = name or self.func.__name__
        else:
            self.name = name or self.__class__.__name__

        self._use_job = use_job
        self._color_output = color_output
        self._logfile = logfile
        self._use_stream = use_stream
        self._stream = None

        # prologue and epilogue statistics/information
        self.started_at = None
        self.pid = None
        self.ended_at = None
        self.elapsed = None

    @property
    def color_output(self):
        return self._color_output

    @property
    def logfile(self):
        return self._logfile

    @property
    def stream(self):
        return self._stream

    @classmethod
    def declare(cls, name=None, func=None, use_job=False,
                color_output=True, use_stream=False, logfile=None):

        job = Job(name=name, func=func, use_job=use_job,
                  color_output=color_output, use_stream=use_stream,
                  logfile=logfile)

        def decorator(f):
            assert job.func is None, "You're attempting to redefine the " \
                                      "inner function of a Job"

            job.name = f.__name__
            job.__doc__ = f.__doc__

            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            job.func = wrapper

            # the decorated function is now a Job
            return job

        return decorator

    @classmethod
    def load_from_pkg(cls, job_name, module_name):
        try:
            module = importlib.import_module(module_name)
            job = getattr(module, job_name)
        except ImportError:
            raise JobImportError(f"Error loading job '{job_name}', could not "
                                 f"import module '{module_name}'")
        except AttributeError:
            raise JobAttributeError(f"Error loading job '{job_name}', no job "
                                    f"called '{job_name}' in module "
                                    f"'{module_name}'")

        if isinstance(job, Job):
            # context 1 : Job class as a decorator (job is an instance of Job)
            pass
            # context 1.2 : Job subclass used as a decorator
            # same behaviour
        elif inspect.isclass(job) and issubclass(job, Job):
            # context 2 : Job subclass used directly through run
            # instantiate
            job = job(name=job_name)

        # other cases
        elif callable(job):
            job = Job.declare(name=job_name)(job)
        else:
            raise JobNotCallable(f"The object '{job_name}' in module "
                                 f"'{module_name}' does not resolve to a "
                                 f"callable")
        assert isinstance(job, Job)
        return job

    @classmethod
    def load(cls, job_ref, module_name=''):

        if isinstance(job_ref, str):
            job = cls.load_from_pkg(job_ref, module_name)
        elif isinstance(job_ref, Job):
            job = job_ref
        elif inspect.isclass(job_ref) and issubclass(job_ref, Job):
            job = job_ref(name=job_ref.__name__)
        else:  # pragma: no cover
            raise BadJobRefError(f"Unexpected type <{type(job_ref).__name__}> "
                                 f"for parameter 'jobref'")

        assert isinstance(job, Job)
        return job

    @classmethod
    def execute(cls, job_ref, *args, module_name='', color_output=None,
                logfile=None, stream=None, **kwargs):
        job = cls.load(job_ref, module_name=module_name)
        return job.run(*args, color_output=color_output, logfile=logfile,
                       stream=stream, **kwargs)

    def prepare(self, color_output, logfile, stream):
        _dispatch_dynamic_methods(self, Job._report_helper, self.name)

        JobReport.register(self.name,
                           color_output=self.color_output,
                           logfile=self.logfile,
                           stream=self.stream)

        if color_output is not None:
            self.reset_color_output(color_output)
        if logfile is not None:
            self.reset_logfile(logfile)
        if stream is not None:
            self.reset_stream(stream)

    def run(self, *args, color_output=None, logfile=None, stream=None,
            **kwargs):

        self.prepare(color_output, logfile, stream)

        _report = None
        if self._use_job:
            args = (*args, self)

        if self._use_stream:
            args = (*args, stream)

        outcome = False
        result = None
        try:
            self.__prologue__()
            result = self._run(*args, **kwargs)
            outcome = True
        except BaseJobException:
            raise
        except _InternalExceptionWrapper as w:
            result = w.exc
            outcome = False
        finally:
            self.__epilogue__(outcome)
            _report = JobReport.get_report(self.name)
            _report.set_pid(self.pid)
            _report.set_result(result)
            _report = JobReport.detach(_report)

        return _report

    def __prologue__(self):
        self.started_at = (dt.datetime.now(), time.perf_counter())
        self.pid = os.getpid()
        self.info(f"Started at {self.started_at[0].strftime('%H:%M:%S')}")

    def __epilogue__(self, success):
        self.ended_at = (dt.datetime.now(), time.perf_counter())
        self.elapsed = self.ended_at[1] - self.started_at[1]
        unit = 's'  # for seconds
        if 0.0 < self.elapsed < 1.0:
            self.elapsed = round(round(self.elapsed, 6) * 1000.0, 3)
            unit = 'ms'  # for milliseconds
        elif self.elapsed > 60.0:
            self.elapsed = round(self.elapsed, 0)
        else:
            self.elapsed = round(self.elapsed, 2)

        self.info(f"Finished at {self.ended_at[0].strftime('%H:%M:%S')}")
        self.info(f"Total elapsed time: {self.elapsed}{unit}")

        if success:
            self.ok("Outcome is a success")
        else:
            self.fail("Outcome is a failure")

    @abstractmethod
    def __run__(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError

    def reset_color_output(self, value):
        self._color_output = value
        JobReport.register(self.name,
                           color_output=value,
                           logfile=self._logfile,
                           stream=self._stream,
                           force=True)

    def reset_logfile(self, value):
        self._logfile = value
        JobReport.register(self.name,
                           color_output=value,
                           logfile=self._logfile,
                           stream=self._stream,
                           force=True)

    def reset_stream(self, value):
        self._stream = value
        JobReport.register(self.name,
                           color_output=self._color_output,
                           logfile=self._logfile,
                           stream=value,
                           force=True)

    def _run(self, *args, **kwargs):

        if self.func:
            func = self.func
        else:
            func = self.__run__

        try:
            result = func(*args, **kwargs)
        except BaseJobException:
            raise
        except Exception as exc:
            self._report_helper(
                self.name,
                logging.ERROR,
                f"Uncaught exception {type(exc).__name__}: {str(exc)}"
            )
            raise _InternalExceptionWrapper(exc, self.name)

        return result

    @staticmethod
    def _report_helper(report_name, level, msg, *args, **kwargs):
        get_report(report_name).report(level, msg, *args, **kwargs)

    @staticmethod
    def _report_helper_default(level, msg, *args, **kwargs):
        frame = inspect.stack()
        name = frame[1].function
        Job._report_helper(name, level, msg, *args, **kwargs)

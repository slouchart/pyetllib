import logging
import copy
import sys

from .exceptions import JobAlreadyRegistered, JobReportNotFound

from ._config import log_levels
from ._internals import _init_dynamic_methods, _dispatch_dynamic_methods

logging.addLevelName(log_levels.OK, 'OK')
logging.addLevelName(log_levels.FAIL, 'FAIL')
logging.addLevelName(log_levels.PROLOGUE, 'PROLOG')
logging.addLevelName(log_levels.EPILOGUE, 'EPILOG')


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

"""The background is set with 40 plus the number of the color, and the
foreground with 30

Below are the sequences need to get colored output"""
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[%dm"
BRIGHT_COLOR_SEQ = "\033[1;%dm"
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[22m"


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ)
        message = message.replace("$BOLD_OFF", BOLD_OFF)
        message = message.replace("$BOLD_ON", BOLD_ON)

    else:
        message = message.replace("$RESET", "")
        message = message.replace("$BOLD_OFF", "")
        message = message.replace("$BOLD_ON", "")
    return message


COLORS = {
    log_levels.ERROR: RED,
    log_levels.WARNING: YELLOW,
    log_levels.INFO: BLUE,
    log_levels.DEBUG: WHITE,
    log_levels.OK: GREEN,
    log_levels.FAIL: MAGENTA,
    log_levels.PROLOGUE: WHITE,
    log_levels.EPILOGUE: WHITE,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, color_output=True):
        logging.Formatter.__init__(self, fmt)
        self.color_output = color_output

    @staticmethod
    def set_str_color(s, color, bright=False):
        if bright:
            return BRIGHT_COLOR_SEQ % (30 + color) + s + RESET_SEQ
        else:
            return COLOR_SEQ % (30 + color) + s + RESET_SEQ

    def format(self, record):
        levelno = record.levelno
        if self.color_output and levelno in COLORS:
            color = COLORS[levelno]

            color_record = copy.deepcopy(record)
            color_record.levelname = self.set_str_color(record.levelname,
                                                        color, bright=True)
            color_record.msg = self.set_str_color(record.msg, color)
        else:
            color_record = record
        return logging.Formatter.format(self, color_record)


@_init_dynamic_methods
class JobReport(logging.Logger):

    FORMAT = "[$BOLD_ON%(name)-20s$BOLD_OFF] " \
             "%(process)d " \
             "%(levelname)-20s " \
             "%(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    PLAIN_FORMAT = formatter_message(FORMAT, False)

    reports = dict()

    def __new__(cls, *args, **kwargs):
        _dispatch_dynamic_methods(cls, cls.report)
        return super().__new__(cls)

    def __init__(self, job_name, color_output=True, logfile=None, stream=None):

        self.name = job_name
        self._on_finalize = None
        stream = stream or sys.stdout
        super().__init__(job_name, level=logging.INFO)

        if color_output:
            selected_format = self.COLOR_FORMAT
        else:
            selected_format = self.PLAIN_FORMAT

        formatter = ColoredFormatter(selected_format,
                                     color_output=color_output)

        console = logging.StreamHandler(stream=stream)
        console.setFormatter(formatter)

        self.addHandler(console)

        if logfile is not None:
            logfile = logging.FileHandler(logfile, encoding='utf-8')
            logfile.setFormatter(ColoredFormatter(self.PLAIN_FORMAT,
                                                  color_output=False))
            self._on_finalize = logfile.close
            self.addHandler(logfile)

        self._pid = None
        self._result = None

    def set_result(self, result):
        self._result = result

    def get_result(self):
        return self._result

    def set_pid(self, pid):
        self._pid = pid

    def get_pid(self):
        return self._pid

    @property
    def success(self):
        return not isinstance(self._result, Exception)

    @property
    def failure(self):
        return isinstance(self._result, Exception)

    def finalize(self):
        if self._on_finalize:
            self._on_finalize()

    @classmethod
    def get_report(cls, name):
        try:
            return cls.reports[name]
        except KeyError:
            raise JobReportNotFound(f"A job report with '{name}' "
                                    f"could not be found "
                                    f"in the registry")

    @classmethod
    def detach(cls, report):
        report.finalize()
        if report.name in cls.reports:
            del cls.reports[report.name]
        return report

    @classmethod
    def register(cls, job_name, color_output=True, logfile=None,
                 stream=None, force=False):

        if job_name in cls.reports:
            if force:
                report = cls.reports[job_name]
                report.finalize()
                del cls.reports[job_name]
            else:  # pragma: no cover
                raise JobAlreadyRegistered(f"A registered job report with "
                                           f"name '{job_name}' already exists")

        cls.reports[job_name] = JobReport(job_name,
                                          color_output=color_output,
                                          logfile=logfile,
                                          stream=stream)

    def report(self, level, msg, *args, **kwargs):
        self.log(level, msg, *args, **kwargs)


get_report = JobReport.get_report

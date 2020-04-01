import enum
import logging


class log_levels(enum.IntEnum):
    OK = 25
    FAIL = 35
    PROLOGUE = 21
    EPILOGUE = 22
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG

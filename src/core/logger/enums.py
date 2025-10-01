from enum import Enum


class Levels(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormats(Enum):
    TIME = "%(asctime)s"
    NAME = "%(name)s"
    LEVEL = "%(levelname)s"
    MESSAGE = "%(message)s"

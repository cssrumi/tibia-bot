from enum import Enum
from typing import Set

import attr


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 2


@attr.s
class LogWriter:

    def write(self, msg: str, lvl: LogLevel):
        raise NotImplementedError()


class Logger:
    _writers: Set[LogWriter] = set()

    @staticmethod
    def log(msg: str, lvl: LogLevel = LogLevel.INFO):
        [writer.write(msg, lvl) for writer in Logger._writers]

    @staticmethod
    def register(writer: LogWriter):
        Logger._writers.add(writer)

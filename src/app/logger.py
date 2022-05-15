import logging
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
    def log(msg: object, lvl: LogLevel = LogLevel.INFO):
        if msg is None:
            return
        if not isinstance(msg, str):
            msg = str(msg)
        [writer.write(msg, lvl) for writer in Logger._writers]

    @staticmethod
    def debug(msg: object):
        Logger.log(msg, lvl=LogLevel.DEBUG)

    @staticmethod
    def info(msg: object):
        Logger.log(msg, lvl=LogLevel.INFO)

    @staticmethod
    def warn(msg: object):
        Logger.log(msg, lvl=LogLevel.WARN)

    @staticmethod
    def error(msg: object):
        Logger.log(msg, lvl=LogLevel.ERROR)

    @staticmethod
    def register(writer: LogWriter):
        Logger._writers.add(writer)


@attr.s(hash=True)
class ConsoleLogWriter(LogWriter):
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)
    logging_map = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARN: logging.WARN,
        LogLevel.ERROR: logging.ERROR,
    }

    def __attrs_post_init__(self):
        Logger.register(self)

    def write(self, msg: str, lvl: LogLevel):
        lvl = ConsoleLogWriter.logging_map.get(lvl)
        logging.log(lvl, msg)


ConsoleLogWriter()

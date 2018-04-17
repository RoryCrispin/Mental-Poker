# coding=utf-8
from enum import IntEnum


class LogLevel(IntEnum):
    VERBOSE = 0
    INFO = 2
    GENERAL = 3
    ERROR = 4


def readable_ident(ident):
    return ident[:4]

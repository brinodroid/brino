from enum import Enum


class BGTaskAction(Enum):
    NONE = "NONE"
    STOPLOSS_EXEC = "STOPLOSS_EXEC"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class BGTaskActionResult(Enum):
    NONE = "NONE"
    GOOD = "GOOD"
    BAD = "BAD"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class BGTaskStatus(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PASS = "PASS"
    FAIL = "FAIL"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class BGTaskDataIdType(Enum):
    WATCHLIST = "WATCHLIST"
    PORTFOLIO = "PORTFOLIO"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

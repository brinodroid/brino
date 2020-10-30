from enum import Enum


class BGTaskAction(Enum):
    NO_ACTION = "NO_ACTION"
    STOPLOSS_COVERED_CALL_TRACKER = "STOPLOSS_COVERED_CALL_TRACKER"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

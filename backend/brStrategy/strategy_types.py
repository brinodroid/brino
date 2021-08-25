from enum import Enum


class StrategyType(Enum):
    DEFAULT = "DEFAULT"
    COVERED_CALL = "COVERED_CALL"
    CALL_OPTION_COVERED_CALL = "CALL_OPTION_COVERED_CALL"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
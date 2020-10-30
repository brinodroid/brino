from enum import Enum


class BGTaskStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    PASS = "PASS"
    FAIL = "FAIL"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

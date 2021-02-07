from enum import Enum


class Status(Enum):
    NONE = "NONE"
    PASS = "PASS"
    FAIL = "FAIL"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
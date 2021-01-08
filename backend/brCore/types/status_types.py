from enum import Enum


class Status(Enum):
    NONE = "NONE"
    GOOD = "GOOD"
    BAD = "BAD"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
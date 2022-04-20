from enum import Enum

class OrderAction(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
from enum import Enum


class ScanStatus(Enum):
    ATTN = "ATTN"
    NONE = "NONE"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class ScanProfile(Enum):
    STOCK = "STOCK"
    CC = "CC" #Covered Call
    CALL = "CALL"
    PUT = "PUT"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

from enum import Enum


class ScanStatus(Enum):
    ATTN = "ATTN"
    MISSING = "MISSING"
    NONE = "NONE"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class ScanProfile(Enum):
    BUY_STOCK = "BUY_STOCK"
    BUY_CALL = "BUY_CALL"
    SELL_CALL = "SELL_CALL"
    BUY_PUT = "BUY_PUT"
    SELL_PUT = "SELL_PUT"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

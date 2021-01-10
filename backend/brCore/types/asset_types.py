from enum import Enum


class AssetTypes(Enum):
    STOCK = "STOCK"
    CALL_OPTION = "CALL"
    PUT_OPTION = "PUT"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PortFolioSource(Enum):
    BRINE = "BRINE"
    BRATE = "BRATE"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

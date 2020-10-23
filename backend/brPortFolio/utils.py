from enum import IntEnum


class ActionTypes(IntEnum):
    ACTION_NOTHING = 0
    ACTION_TRACK = 1

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class AssetTypes(IntEnum):
    STOCK = 1
    OPTION = 2

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class TransactionTypes(IntEnum):
    BUY = 1
    SELL = 2
    DIVIDENT = 3
    FEE = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

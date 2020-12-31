from enum import Enum


class AssetTypes(Enum):
    STOCK = "STOCK"
    CALL_OPTION = "CALL"
    PUT_OPTION = "PUT"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

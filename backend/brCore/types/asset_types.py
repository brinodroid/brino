from enum import Enum


class AssetTypes(Enum):
    STOCK = "STOCK"
    OPTION = "OPTION"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

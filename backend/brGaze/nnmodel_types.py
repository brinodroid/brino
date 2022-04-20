from enum import Enum


class NNModelTypes(Enum):
    LSTM = "LSTM"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
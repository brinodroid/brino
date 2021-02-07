from common.types.asset_types import PortFolioSource
from .brine_adapter import BrineAdapter


#We just need one instance to be kept. Hence using a globally created list
client_list = {
    PortFolioSource.BRINE.value: BrineAdapter(),
    PortFolioSource.BRATE.value: None
}


def get_client(source=PortFolioSource.BRINE.value):

    return client_list[source]

import brine
from brCore.types.asset_types import PortFolioSource, AssetTypes, TransactionType


class BrineAdapter:
    __option_data_type_lut = {
        'call': AssetTypes.CALL_OPTION.value,
        'put': AssetTypes.PUT_OPTION.value
    }

    __transaction_type_lut = {
        'long': TransactionType.BUY.value,
        'short': TransactionType.SELL.value
    }

    def __init__(self):
        brine.login()

    def get_my_options_list(self):
        res_option_list = []
        option_list = brine.options.get_open_option_positions()
        for option in option_list:
            res_option = {}
            res_option['client'] = PortFolioSource.BRINE.value
            res_option['average_price'] = option['average_price']
            res_option['created_at'] = option['created_at']
            res_option['chain_id'] = option['chain_id']
            res_option['chain_symbol'] = option['chain_symbol']
            res_option['id'] = option['id']
            res_option['type'] = option['type']
            res_option['quantity'] = option['quantity']
            res_option['trade_value_multiplier'] = option['trade_value_multiplier']
            res_option['option_id'] = option['option_id']
            res_option['brino_transaction_type'] = self.__transaction_type_lut[option['type']]
            if res_option['brino_transaction_type'] == TransactionType.BUY.value:
                res_option['brino_entry_price'] = float(res_option['average_price']);
            else:
                #Gives negative value for price for selling transactions. Make it positve
                res_option['brino_entry_price'] = -float(res_option['average_price']);

            res_option_list.append(res_option)

        return res_option_list

    def get_option_data(self, option_id):
        option_data = brine.options.get_option_instrument_data_by_id(option_id)
        # Modify the asset type
        option_data['brino_asset_type'] = self.__option_data_type_lut[option_data['type']]
        return option_data

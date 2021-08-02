import re
import logging
import brine
from common.types.asset_types import PortFolioSource, AssetTypes, TransactionType

logger = logging.getLogger('django')


class BrineAdapter:
    __option_data_type_lut = {
        'call': AssetTypes.CALL_OPTION.value,
        'put': AssetTypes.PUT_OPTION.value
    }

    __transaction_type_lut = {
        'long': TransactionType.BUY.value,
        'buy': TransactionType.BUY.value,
        'short': TransactionType.SELL.value,
        'sell': TransactionType.SELL.value
    }

    __opening_strategy_transaction_type_lut = {
        'long_put': TransactionType.BUY.value,
        'long_call': TransactionType.BUY.value,
        'short_put': TransactionType.SELL.value,
        'short_call': TransactionType.SELL.value
    }

    __opening_strategy_transaction_type_lut = {
        'long_put': TransactionType.BUY.value,
        'long_call': TransactionType.BUY.value,
        'short_put': TransactionType.SELL.value,
        'short_call': TransactionType.SELL.value
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
                res_option['brino_entry_price'] = float(
                    res_option['average_price'])
            else:
                # Gives negative value for price for selling transactions. Make it positve
                res_option['brino_entry_price'] = - \
                    float(res_option['average_price'])

            res_option_list.append(res_option)

        return res_option_list

    def get_option_data(self, option_id):
        option_data = brine.options.get_option_instrument_data_by_id(option_id)
        # Modify the asset type
        option_data['brino_asset_type'] = self.__option_data_type_lut[option_data['type']]
        return option_data

    def get_my_stock_list(self):
        res_stock_list = []
        stock_list = brine.account.get_open_stock_positions()
        for stock in stock_list:
            res_stock = {}
            res_stock['client'] = PortFolioSource.BRINE.value
            res_stock['brino_asset_type'] = AssetTypes.STOCK.value
            res_stock['brino_transaction_type'] = TransactionType.BUY.value

            res_stock['brino_entry_price'] = float(stock['average_buy_price'])
            res_stock['quantity'] = stock['quantity']
            res_stock['shares_available_for_exercise'] = stock['shares_available_for_exercise']
            res_stock['shares_held_for_options_collateral'] = stock['shares_held_for_options_collateral']
            res_stock['instrument_url'] = stock['instrument']
            res_stock['created_at'] = stock['created_at']

            # Extract the instrument id from the url
            res_stock['instrument_id'] = re.search(
                'https://api.robinhood.com/instruments/(.+?)/', stock['instrument']).group(1)

            res_stock_list.append(res_stock)

        return res_stock_list

    def get_stock_instrument_data(self, instrument_url):
        stock_data = brine.stocks.get_instrument_by_url(instrument_url)
        return stock_data

    def get_ticker_price_dict(self, uniq_ticker_list, includeExtendedHours):
        try:
            current_price_list = brine.get_latest_price(
                uniq_ticker_list, includeExtendedHours=includeExtendedHours)

            if len(uniq_ticker_list) != len(current_price_list):
                # Something is wrong as the lists size are mismatching
                logger.error('get_stock_current_price: list size mismatch uniq_ticker_list: {}, current_price_list: {}'
                             .format(len(uniq_ticker_list), len(current_price_list)))
                return None

            # return as a dictionary for easy lookup
            ticker_price_dict = {}
            i = 0
            while i < len(current_price_list):
                ticker_price_dict[uniq_ticker_list[i]
                                  ] = float(current_price_list[i])
                i += 1

            return ticker_price_dict

        except Exception as e:
            logger.error(
                'get_stock_current_price: Exception: {}'.format(repr(e)))
            return None

    def get_option_price(self, ticker, expiry, strike, type):
        # TODO: Investigate why option price is returned as dictionary list
        return brine.options.get_option_market_data(ticker, expiry, strike, type)

    def __safe_float(self, float_string):
        try:
            f = float(float_string)
            return f
        except:
            logger.info('__safe_float: Not valid number =%s', float_string)
        return 0

    def __convert_order_to_brine(self, order):
        res_order = {}
        res_order['client'] = PortFolioSource.BRINE.value

        res_order['brino_entry_price'] = self.__safe_float(order['price'])
        res_order['quantity'] = order['quantity']
        res_order['id'] = order['id']
        res_order['state'] = order['state']
        res_order['created_at'] = order['created_at']
        res_order['updated_at'] = order['updated_at']

        if 'chain_id' in order:
            # This is an option order
            res_order['chain_id'] = order['chain_id']
            res_order['chain_symbol'] = order['chain_symbol']
            res_order['opening_strategy'] = order['opening_strategy']
            res_order['closing_strategy'] = order['closing_strategy']

            res_legs_list = []
            for leg in order['legs']:
                res_leg = {}
                res_leg['brino_transaction_type'] = self.__transaction_type_lut[leg['side']]
                res_leg['id'] = leg['id']
                res_leg['instrument_url'] = leg['option']
                # Extract the instrument id from the url
                res_leg['instrument_id'] = re.search(
                    'https://api.robinhood.com/options/instruments/(.+?)/', leg['option']).group(1)

            res_legs_list.append(res_leg)
            res_order['res_legs_list'] = res_legs_list
        else:
            # This is a stock order
            res_order['brino_asset_type'] = AssetTypes.STOCK.value
            res_order['brino_transaction_type'] = self.__transaction_type_lut[order['side']]
            res_order['instrument_url'] = order['instrument']
            # Extract the instrument id from the url
            res_order['instrument_id'] = re.search(
                'https://api.robinhood.com/instruments/(.+?)/', order['instrument']).group(1)

        return res_order


    def get_open_option_orders(self):
        order_list = brine.orders.get_all_open_option_orders()
        res_order_list = []

        for order in order_list:
            res_order_list.append(self.__convert_order_to_brine(order))

        return res_order_list

    def get_open_option_order_status(self, order_id):
        order = brine.orders.get_option_order_info(order_id)
        return self.__convert_order_to_brine(order)

    def get_open_stock_orders(self):
        order_list = brine.orders.get_all_open_stock_orders()
        res_order_list = []

        for order in order_list:
            res_order_list.append(self.__convert_order_to_brine(order))

        return res_order_list

    def get_open_stock_order_status(self, order_id):
        order = brine.orders.get_stock_order_info(order_id)
        return self.__convert_order_to_brine(order)

    def order_stock_buy_limit(self, symbol, quantity, limit_price):
        order = brine.orders.order_buy_limit(symbol, quantity, limit_price, extendedHours=True)
        return self.__convert_order_to_brine(order)

    def order_stock_sell_limit(self, symbol, quantity, limit_price):
        order = brine.orders.order_sell_limit(symbol, quantity, limit_price, extendedHours=True)
        return self.__convert_order_to_brine(order)

    def order_stock_buy_market(self, symbol, quantity, limit_price):
        order = brine.orders.order_buy_market(symbol, quantity, limit_price, extendedHours=True)
        return order

    def order_stock_sell_market(self, symbol, quantity, limit_price):
        order = brine.orders.order_sell_market(symbol, quantity, limit_price, extendedHours=True)
        return order

    def order_option_buy_open_limit(self, creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType):
        order = brine.orders.order_buy_option_limit('open', creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType)
        return order

    def order_option_buy_close_limit(self, creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType):
        order = brine.orders.order_buy_option_limit('close', creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType)
        return order

    def order_option_buy_stop_limit(self, creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType):
        order = brine.orders.order_buy_option_stop_limit('close', creditOrDebit, price, price, symbol, quantity, expirationDate, strike, optionType)
        return order

    def order_option_sell_open_limit(self, creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType):
        order = brine.orders.order_sell_option_limit('open', creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType)
        return order

    def order_option_sell_close_limit(self, creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType):
        order = brine.orders.order_sell_option_limit('close', creditOrDebit, price, symbol, quantity, expirationDate, strike, optionType)
        return order
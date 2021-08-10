import logging
from datetime import datetime, timedelta
from common.types.asset_types import AssetTypes
from brCore.models import WatchList
from brHistory.models import CallOptionData, PutOptionData, StockData
import common.utils as utils
from common.client.Factory import get_client
from django.utils import timezone

logger = logging.getLogger('django')

def create_stock_history(watchlist):
    if watchlist.asset_type != AssetTypes.STOCK.value:
        logger.error('create_stock_history: Wrong assettype. Ignoring watchlist {}'.format(watchlist))
        return None

    date = timezone.now().date()

    try:
        stock_data_list = StockData.objects.filter(date=date, watchlist_id=watchlist.id)
        if len(stock_data_list)>0:
            # stock_data exists for the same date
            return stock_data_list[0]

        # If the stock_data does not exists, continue
    except StockData.DoesNotExist:
        # StockData history does not exist. Add a new entry for th date
        logger.info('create_stock_history: stock_data not found for watchlist_id {}'.format(
            watchlist.id))


    # Try adding the data
    client = get_client()
    stock_raw_data = client.get_stock_data(watchlist.ticker,
                        interval='day',
                        span='week')
    if len(stock_raw_data) < 5:
        logger.info('create_stock_history: stock_raw_data not found for watchlist_id {}'.format(
            watchlist.id))
        return None

    stock_data = stock_raw_data[4]
    if not stock_data:
        logger.info('create_stock_history: stock_raw_data not found for watchlist_id {}'.format(
            watchlist.id))
        return None

    return _update_stockdata_table(watchlist.id, stock_data)

def stock_history_update():
    try:
        watchlist_list = WatchList.objects.filter(
            asset_type=AssetTypes.STOCK.value)
    except WatchList.DoesNotExist:
        # Nothing to scan
        logger.info('stock_history_update: No watchlist found')
        return

    date = timezone.now().date()
    for watchlist in watchlist_list:
        logger.info('stock_history_update: watchlist {}'.format(watchlist))
        create_stock_history(watchlist)

    return


def create_option_history(watchlist):
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        return create_call_option_history(watchlist)
    
    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        return create_put_option_history(watchlist)

    logger.error('create_option_history: Wrong assettype. Ignoring watchlist {}'.format(watchlist))
    return None



def create_call_option_history(watchlist):
    date = timezone.now().date()

    try:
        call_option_data = CallOptionData.objects.filter(date=date, watchlist_id=watchlist.id)
        # call_option_data exists for the same date
        return call_option_data
    except CallOptionData.DoesNotExist:
        #Put option history does not exist. Add a new entry for th date
        logger.info('create_call_option_history: call_option_data not found for watchlist_id {}'.format(
            watchlist.id))

    client = get_client()

    option_raw_data = client.get_option_price(watchlist.ticker,
                        str(watchlist.option_expiry),
                        str(watchlist.option_strike),
                        'call')
    option_data = option_raw_data[0][0]

    return _update_call_option_table(watchlist_id, option_data)

def _update_call_option_table(watchlist_id, option_data):
    call_option_data = CallOptionData(watchlist_id=watchlist_id,
        mark_price=utils.safe_float(option_data['mark_price']),
        ask_price=utils.safe_float(option_data['ask_price']),
        bid_price=utils.safe_float(option_data['bid_price']),
        high_price=utils.safe_float(option_data['high_price']),
        low_price=utils.safe_float(option_data['low_price']),
        last_trade_price=utils.safe_float(option_data['last_trade_price']),

        open_interest=utils.safe_int(option_data['open_interest']),
        volume=utils.safe_int(option_data['volume']),
        ask_size=utils.safe_int(option_data['ask_size']),
        bid_size=utils.safe_int(option_data['bid_size']),

        delta=utils.safe_float(option_data['delta']),
        gamma=utils.safe_float(option_data['gamma']),
        implied_volatility=utils.safe_float(option_data['implied_volatility']),
        rho=utils.safe_float(option_data['rho']),
        theta=utils.safe_float(option_data['theta']),
        vega=utils.safe_float(option_data['vega'])
                    )
    call_option_data.save()
    return call_option_data

def create_put_option_history(watchlist):
    date = timezone.now().date()

    try:
        put_option_data = PutOptionData.objects.filter(date=date, watchlist_id=watchlist.id)
        # Put option history for the same date already exists
        return put_option_data
    except PutOptionData.DoesNotExist:
        #Put option history does not exist. Add a new entry for th date
        logger.info('create_put_option_history: put_option_data not found for watchlist_id {}'.format(
            watchlist.id))

    client = get_client()

    option_raw_data = client.get_option_price(watchlist.ticker,
                        str(watchlist.option_expiry),
                        str(watchlist.option_strike),
                        'put')
    option_data = option_raw_data[0][0]

    return _update_put_option_table(watchlist_id, option_data)

def _update_put_option_table(watchlist_id, option_data):
    put_option_data = PutOptionData(watchlist_id=watchlist_id,
        mark_price=utils.safe_float(option_data['mark_price']),
        ask_price=utils.safe_float(option_data['ask_price']),
        bid_price=utils.safe_float(option_data['bid_price']),
        high_price=utils.safe_float(option_data['high_price']),
        low_price=utils.safe_float(option_data['low_price']),
        last_trade_price=utils.safe_float(option_data['last_trade_price']),

        open_interest=utils.safe_int(option_data['open_interest']),
        volume=utils.safe_int(option_data['volume']),
        ask_size=utils.safe_int(option_data['ask_size']),
        bid_size=utils.safe_int(option_data['bid_size']),

        delta=utils.safe_float(option_data['delta']),
        gamma=utils.safe_float(option_data['gamma']),
        implied_volatility=utils.safe_float(option_data['implied_volatility']),
        rho=utils.safe_float(option_data['rho']),
        theta=utils.safe_float(option_data['theta']),
        vega=utils.safe_float(option_data['vega'])
        )
    put_option_data.save()

    return put_option_data


def _update_stockdata_table(watchlist_id, stock_data_in):
    stock_data = StockData(watchlist_id=watchlist_id,
        high_price=utils.safe_float(stock_data_in['high_price']),
        low_price=utils.safe_float(stock_data_in['low_price']),
        open_price=utils.safe_float(stock_data_in['open_price']),
        close_price=utils.safe_float(stock_data_in['close_price']),
        volume=utils.safe_float(stock_data_in['volume']),
        date=utils.convert_datetime_string_to_django_time(stock_data_in['begins_at'])
        )
    stock_data.save()
    return stock_data

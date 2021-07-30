import logging
from datetime import datetime, timedelta
from common.types.asset_types import AssetTypes
from brCore.models import WatchList
from brHistory.models import CallOptionData, PutOptionData
import common.utils as utils
from common.client.Factory import get_client
from django.utils import timezone


logger = logging.getLogger('django')

def create_option_history(watchlist):
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        return create_call_option_history(watchlist)
    
    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        return create_put_option_history(watchlist)


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
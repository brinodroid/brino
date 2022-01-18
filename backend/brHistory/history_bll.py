import logging
from datetime import datetime, timedelta, date
from common.types.asset_types import AssetTypes
from brCore.models import WatchList
from brHistory.models import CallOptionData, PutOptionData, StockData
import common.utils as utils
from common.client.Factory import get_client
from django.utils import timezone
from brHistory.crawler import Crawler
import brCore.watchlist_bll as watchlist_bll

logger = logging.getLogger('django')

def save_history():
    # TODO: Need logic to ignore weekdays??

    Crawler.getInstance().save_option_history()

    # Save stock history
    stock_history_update()


def create_stock_history(watchlist):
    if watchlist.asset_type != AssetTypes.STOCK.value:
        logger.error(
            'create_stock_history: Wrong assettype. Ignoring watchlist {}'.format(watchlist))
        return None

    date = timezone.now().date()
    try:
        stock_data_list = StockData.objects.filter(
            date=date, watchlist_id=watchlist.id)
        if len(stock_data_list) > 0:
            # stock_data exists for the same date
            return stock_data_list[0]

        # If the stock_data does not exists, continue
    except StockData.DoesNotExist:
        # StockData history does not exist. Add a new entry for th date
        logger.info('create_stock_history: stock_data not found for watchlist_id {}'.format(
            watchlist.id))

    # Try adding the data
    client = get_client()

    # Only gets you todays info
    stock_raw_data_list = client.get_fundamentals(watchlist.ticker)
    if stock_raw_data_list is None:
        logger.error('create_stock_history: got none data {} for watchlist.id {}'.format(
        stock_raw_data_list, watchlist.id))
        return None

    today_string = utils.today_begin_utctime_string()

    # Update also the low frequency data into watch list

    return _update_stockdata_table(watchlist.id, stock_raw_data_list, today_string)


def stock_history_update():
    watchlist_list = watchlist_bll.get_stock_watchlist()

    for watchlist in watchlist_list:
        logger.info('stock_history_update: watchlist {}'.format(watchlist))
        create_stock_history(watchlist)

    return


def create_option_history(watchlist):
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        return create_call_option_history(watchlist)

    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        return create_put_option_history(watchlist)

    logger.error(
        'create_option_history: Wrong assettype. Ignoring watchlist {}'.format(watchlist))
    return None

def get_history(watchlist, past_days):
    logger.info('get_history: watchlist {} past_days {}'.format(watchlist, past_days))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=past_days)

    if watchlist.asset_type == AssetTypes.STOCK.value:
        history_list = StockData.objects.filter(watchlist_id=watchlist.id) \
                                        .filter(date__range=[start_date, end_date])\
                                        .order_by('date')
        return history_list

    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        history_list = CallOptionData.objects.filter(watchlist_id=watchlist.id) \
                                        .filter(date__range=[start_date, end_date])\
                                        .order_by('date')
        return history_list

    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        history_list = PutOptionData.objects.filter(watchlist_id=watchlist.id) \
                                        .filter(date__range=[start_date, end_date])\
                                        .order_by('date')
        return history_list

    return None

def get_history_on_date(watchlist, on_date):
    logger.info('get_history_on_date: watchlist {} on_date {}'.format(watchlist, on_date))
    
    if watchlist.asset_type == AssetTypes.STOCK.value:
        history_list = StockData.objects.filter(watchlist_id=watchlist.id) \
                                        .filter(date=on_date)
        if history_list.exists():
            # We got history for the date
            return history_list[0]
        # No data
        return None
    
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        history_list = CallOptionData.objects.filter(watchlist_id=watchlist.id) \
                                        .filter(date=on_date)
        if history_list.exists():
            # We got history for the date
            return history_list[0]
        # No data
        return None

    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        history_list = PutOptionData.objects.filter(watchlist_id=watchlist.id) \
                                        .filter(date=on_date)
        if history_list.exists():
            # We got history for the date
            return history_list[0]
        # No data
        return None

    return None

def create_call_option_history(watchlist):
    date = timezone.now().date()

    try:
        call_option_data = CallOptionData.objects.filter(
            date=date, watchlist_id=watchlist.id)
        # call_option_data exists for the same date
        return call_option_data
    except CallOptionData.DoesNotExist:
        # Put option history does not exist. Add a new entry for th date
        logger.info('create_call_option_history: call_option_data not found for watchlist_id {}'.format(
            watchlist.id))

    client = get_client()

    option_raw_data = client.get_option_price(watchlist.ticker,
                                              str(watchlist.option_expiry),
                                              str(watchlist.option_strike),
                                              'call')
    option_data = option_raw_data[0][0]

    return _update_call_option_table(watchlist.id, option_data)


def _update_call_option_table(watchlist_id, option_data):
    call_option_data = CallOptionData(watchlist_id=watchlist_id,
                                      mark_price=utils.safe_float(
                                          option_data['mark_price']),
                                      ask_price=utils.safe_float(
                                          option_data['ask_price']),
                                      bid_price=utils.safe_float(
                                          option_data['bid_price']),
                                      high_price=utils.safe_float(
                                          option_data['high_price']),
                                      low_price=utils.safe_float(
                                          option_data['low_price']),
                                      last_trade_price=utils.safe_float(
                                          option_data['last_trade_price']),

                                      open_interest=utils.safe_int(
                                          option_data['open_interest']),
                                      volume=utils.safe_int(
                                          option_data['volume']),
                                      ask_size=utils.safe_int(
                                          option_data['ask_size']),
                                      bid_size=utils.safe_int(
                                          option_data['bid_size']),

                                      delta=utils.safe_float(
                                          option_data['delta']),
                                      gamma=utils.safe_float(
                                          option_data['gamma']),
                                      implied_volatility=utils.safe_float(
                                          option_data['implied_volatility']),
                                      rho=utils.safe_float(option_data['rho']),
                                      theta=utils.safe_float(
                                          option_data['theta']),
                                      vega=utils.safe_float(
                                          option_data['vega'])
                                      )
    call_option_data.save()
    return call_option_data


def create_put_option_history(watchlist):
    date = timezone.now().date()

    try:
        put_option_data = PutOptionData.objects.filter(
            date=date, watchlist_id=watchlist.id)
        # Put option history for the same date already exists
        return put_option_data
    except PutOptionData.DoesNotExist:
        # Put option history does not exist. Add a new entry for th date
        logger.info('create_put_option_history: put_option_data not found for watchlist_id {}'.format(
            watchlist.id))

    client = get_client()

    option_raw_data = client.get_option_price(watchlist.ticker,
                                              str(watchlist.option_expiry),
                                              str(watchlist.option_strike),
                                              'put')
    option_data = option_raw_data[0][0]

    return _update_put_option_table(watchlist.id, option_data)


def _update_put_option_table(watchlist_id, option_data):
    put_option_data = PutOptionData(watchlist_id=watchlist_id,
                                    mark_price=utils.safe_float(
                                        option_data['mark_price']),
                                    ask_price=utils.safe_float(
                                        option_data['ask_price']),
                                    bid_price=utils.safe_float(
                                        option_data['bid_price']),
                                    high_price=utils.safe_float(
                                        option_data['high_price']),
                                    low_price=utils.safe_float(
                                        option_data['low_price']),
                                    last_trade_price=utils.safe_float(
                                        option_data['last_trade_price']),

                                    open_interest=utils.safe_int(
                                        option_data['open_interest']),
                                    volume=utils.safe_int(
                                        option_data['volume']),
                                    ask_size=utils.safe_int(
                                        option_data['ask_size']),
                                    bid_size=utils.safe_int(
                                        option_data['bid_size']),

                                    delta=utils.safe_float(
                                        option_data['delta']),
                                    gamma=utils.safe_float(
                                        option_data['gamma']),
                                    implied_volatility=utils.safe_float(
                                        option_data['implied_volatility']),
                                    rho=utils.safe_float(option_data['rho']),
                                    theta=utils.safe_float(
                                        option_data['theta']),
                                    vega=utils.safe_float(option_data['vega'])
                                    )
    put_option_data.save()

    return put_option_data


def _update_stockdata_table(watchlist_id, stock_data_in, today_string):
    stock_data = StockData(watchlist_id=watchlist_id,
                           high_price=stock_data_in['high_price'],
                           low_price=stock_data_in['low_price'],
                           open_price=stock_data_in['open_price'],
                           close_price=stock_data_in['close_price'],
                           volume=stock_data_in['volume'],
                           average_volume=stock_data_in['average_volume'],
                           average_volume_2_weeks=stock_data_in['average_volume_2_weeks'],
                           dividend_yield=stock_data_in['dividend_yield'],
                           market_cap=stock_data_in['market_cap'],
                           pb_ratio=stock_data_in['pb_ratio'],
                           pe_ratio=stock_data_in['pe_ratio'],
                           low_52_weeks=stock_data_in['low_52_weeks'],
                           high_52_weeks=stock_data_in['high_52_weeks'],
                           num_employees=stock_data_in['num_employees'],
                           shares_outstanding=stock_data_in['shares_outstanding'],
                           float=stock_data_in['float'],
                           date=utils.convert_datetime_string_to_django_time(today_string)
                           )
    stock_data.save()
    return stock_data

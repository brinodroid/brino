import logging
import sys
from datetime import datetime, timedelta, date
from brCore.models import WatchList
from brCore.serializers.watchlist import WatchListSerializer
from common.types.asset_types import AssetTypes
from common.client.Factory import get_client
import common.utils as utils

logger = logging.getLogger('django')


def is_option(watchlist):
    return _is_option(watchlist.asset_type)


def create_watchlist_for_call_option_above_price(watchlist, price, expiry):

    # Get the closest monthly call option above price
    client = get_client()

    # Get call option strike price at 5 levels beyond latest price
    options_list = client.get_all_options_on_expiry_date(
        watchlist.ticker, expiry, 'call')
    if options_list == None or len(options_list) == 0:
        logger.error(
            'create_watchlist_for_call_option_above_price: get_all_options_on_expiry_date() for watchlist {} didnt get any data'
            .format(watchlist))
        return None

    closest_option = __get_closest_strike_above_price(options_list, price)
    if closest_option == None:
        logger.error(
            'create_watchlist_for_call_option_above_price: __get_closest_strike_above_price() for watchlist {} didnt get any data'
            .format(watchlist))
        return None

    try:
        # Check if option exists in watchlist
        watchlist = WatchList.objects.get(asset_type=AssetTypes.CALL_OPTION.value,
                                          ticker=watchlist.ticker,
                                          option_strike=closest_option['strike_price'],
                                          option_expiry=closest_option['expiration_date'])

        # Already in DB. Just return it
        return watchlist
    except WatchList.DoesNotExist:
        logger.info(
            'create_watchlist_for_call_option_above_price: closest_option {} needs to be created'
            .format(closest_option))

        # INTENTIONAL FALL DOWN
    # Create a new watchlist
    watchlist = WatchList(asset_type=AssetTypes.CALL_OPTION.value,
                            ticker=watchlist.ticker,
                            option_strike=closest_option['strike_price'],
                            option_expiry=closest_option['expiration_date'])
    watchlist.save()
    return watchlist


def create_watchlist_for_put_option_below_price(watchlist, price, expiry):
    # Get the closest monthly call option above price

    client = get_client()

    # Get call option strike price at 5 levels beyond latest price
    options_list = client.get_all_options_on_expiry_date(
        watchlist.ticker, expiry, 'put')
    if options_list == None or len(options_list) == 0:
        logger.error(
            'create_watchlist_for_put_option_below_price: get_all_options_on_expiry_date() for watchlist {} didnt get any data'
            .format(watchlist))
        return None

    closest_option = __get_closest_strike_below_price(options_list, price)
    if closest_option == None:
        logger.error(
            'create_watchlist_for_put_option_below_price: __get_closest_strike_above_price() for watchlist {} didnt get any data'
            .format(watchlist))
        return None

    try:
        # Check if option exists in watchlist
        watchlist = WatchList.objects.get(asset_type=AssetTypes.PUT_OPTION.value,
                                          ticker=watchlist.ticker,
                                          option_strike=closest_option['strike_price'],
                                          option_expiry=closest_option['expiration_date'])

        # Already in DB. Just return it
        return watchlist
    except WatchList.DoesNotExist:
        logger.info(
            'create_watchlist_for_put_option_below_price: closest_option {} needs to be created'
            .format(closest_option))

        # INTENTIONAL FALL DOWN
    # Create a new watchlist
    watchlist = WatchList(asset_type=AssetTypes.PUT_OPTION.value,
                            ticker=watchlist.ticker,
                            option_strike=closest_option['strike_price'],
                            option_expiry=closest_option['expiration_date'])
    watchlist.save()
    return watchlist


def get_all_watchlists_for_ticker(ticker):
    watchlists_for_ticker = WatchList.objects.filter(ticker=ticker)
    return watchlists_for_ticker


def get_watchlist_latest_price(watchlist, only_mark_price=False, includeExtendedHours=True):
    client = get_client()

    if not is_option(watchlist):
        # This has to be a stock
        latest_ticker_price_dict = client.get_ticker_price_dict(
            [watchlist.ticker], includeExtendedHours)

        return latest_ticker_price_dict[watchlist.ticker]

    # This is an option
    optionType = 'call'
    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        optionType = 'put'

    option_raw_data = client.get_option_price(watchlist.ticker,
                                              str(watchlist.option_expiry),
                                              str(watchlist.option_strike), optionType)

    option_data = option_raw_data[0][0]
    if only_mark_price:
        return utils.safe_float(option_data['mark_price'])

    return utils.safe_float(option_data['mark_price']), utils.safe_float(option_data['ask_price']), utils.safe_float(option_data['bid_price'])


def get_watchlist(asset_type, ticker, option_strike, option_expiry):
    watchlist = WatchList.objects.get(asset_type=asset_type,
                                      ticker=ticker,
                                      option_strike=option_strike,
                                      option_expiry=option_expiry)
    return watchlist


def get_watchlist(watchlist_id):
    watchlist = WatchList.objects.get(pk=int(watchlist_id))
    return watchlist

def get_stock_watchlist():
    try:
        watchlist_list = WatchList.objects.filter(
            asset_type=AssetTypes.STOCK.value)
        return watchlist_list

    except WatchList.DoesNotExist:
        logger.info('get_stock_watchlist: No watchlist found')

    return None

def create_watchlist_if_not_exists_from_json(watchlist_json):
    # Create a new watchlist
    serializer = WatchListSerializer(data=watchlist_json)
    if serializer.is_valid() == False:
        logger.error(serializer.errors)
        return None

    # Check if its an option
    if _is_option(serializer.validated_data['asset_type']):
        return create_option_watchlist_if_not_exists(serializer.validated_data)

    # stock
    logger.error("check if stock is in DB")
    return _create_stock_watchlist_if_not_exists(serializer.validated_data)


def _is_option(asset_type):
    if asset_type == AssetTypes.CALL_OPTION.value or asset_type == AssetTypes.PUT_OPTION.value:
        return True
    return False


def create_option_watchlist_if_not_exists(option_data):
    watchlist = None
    ticker = option_data['ticker'].upper()
    try:
        watchlist = WatchList.objects.get(asset_type=option_data['asset_type'],
                                          ticker=ticker,
                                          option_strike=option_data['option_strike'],
                                          option_expiry=option_data['option_expiry'])
        # Already in DB. Just return it
        return watchlist

    except WatchList.DoesNotExist:
        # Create a new watchlist
        watchlist = WatchList(asset_type=option_data['asset_type'],
                              ticker=ticker,
                              option_strike=option_data['option_strike'],
                              option_expiry=option_data['option_expiry'])
        watchlist.save()

    return watchlist


def _create_stock_watchlist_if_not_exists(stock_data):
    watchlist = None
    ticker = stock_data['ticker'].upper()
    try:
        watchlist = WatchList.objects.get(asset_type=stock_data['asset_type'],
                                          ticker=ticker)
        # Already in DB. Just return it
        return watchlist

    except WatchList.DoesNotExist:
        # Create a new watchlist
        watchlist = WatchList(asset_type=stock_data['asset_type'],
                              ticker=ticker)
        watchlist.save()

    return watchlist


def __get_closest_strike_above_price(option_list, price):
    min = sys.float_info.max
    closest_option = None
    for option in option_list:
        if option is None:
            logger.error(
                'get_closest_strike_above_price: option {} looks is None'
                .format(option))
            continue

        if 'strike_price' not in option:
            logger.error(
                'get_closest_strike_above_price: option {} looks invalid'
                .format(option))
            continue

        strike_price = utils.safe_float(option['strike_price'])
        if strike_price == None:
            logger.error(
                'get_closest_strike_above_price: option {} looks invalid'
                .format(option))
            continue

        if price >= strike_price:
            # the strike price is lower, skip it
            continue

        # Strike price is more than the latest_price
        if min > (strike_price - price):
            issue_date = datetime.strptime(
                option['issue_date'], utils.option_expiry_date_strpfmt_string).date()
            if issue_date < date.today():
                min = strike_price - price
                closest_option = option
            else:
                logger.error(
                    'get_closest_strike_above_price: option {} is untradable'
                    .format(option))

    return closest_option


def __get_closest_strike_below_price(option_list, price):
    min = sys.float_info.max
    closest_option = None
    for option in option_list:
        if option is None:
            logger.error(
                '__get_closest_strike_below_price: option {} looks is None'
                .format(option))
            continue

        if 'strike_price' not in option:
            logger.error(
                '__get_closest_strike_below_price: option {} looks invalid'
                .format(option))
            continue

        strike_price = utils.safe_float(option['strike_price'])
        if strike_price == None:
            logger.error(
                '__get_closest_strike_below_price: option {} looks invalid'
                .format(option))
            return None

        if price <= strike_price:
            # the strike price is lower, skip it
            continue

        # Strike price is more than the latest_price
        if min > (price - strike_price):
            issue_date = datetime.strptime(
                option['issue_date'], utils.option_expiry_date_strpfmt_string).date()
            if issue_date < date.today():
                min = price - strike_price
                closest_option = option
            else:
                logger.error(
                    '__get_closest_strike_below_price: option {} is not tradable yet'
                    .format(option))

    return closest_option

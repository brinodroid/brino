import logging
from datetime import datetime, timedelta
from brCore.models import WatchList
from brCore.serializers.watchlist import WatchListSerializer
from common.types.asset_types import AssetTypes
from common.client.Factory import get_client
import common.utils as utils

logger = logging.getLogger('django')


def is_option(watchlist):
    return _is_option(watchlist.asset_type)

def get_all_watchlists_for_ticker(ticker):
    watchlists_for_ticker = WatchList.objects.filter(ticker=ticker)
    return watchlists_for_ticker

def get_watchlist_latest_price(watchlist, only_mark_price=False):
    client = get_client()

    if not is_option(watchlist):
        # This has to be a stock
        latest_ticker_price_dict = client.get_ticker_price_dict([watchlist.ticker], True)

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

def create_watchlist_if_not_exists_from_json(watchlist_json):
    # Create a new watchlist
    serializer = WatchListSerializer(data=watchlist_json)
    if serializer.is_valid() == False:
        logger.error(serializer.errors)
        return None

    # Check if its an option
    if _is_option(serializer.validated_data['asset_type']):
        return _create_option_watchlist_if_not_exists(serializer.validated_data)

    # stock
    logger.error("check if stock is in DB")
    return _create_stock_watchlist_if_not_exists(serializer.validated_data)


def _is_option(asset_type):
    if asset_type == AssetTypes.CALL_OPTION.value or asset_type == AssetTypes.PUT_OPTION.value:
        return True
    return False

def _create_option_watchlist_if_not_exists(option_data):
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

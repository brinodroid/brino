import logging
from datetime import datetime, timedelta
from brCore.models import WatchList
from common.types.asset_types import AssetTypes
from brCore.serializers.watchlist import WatchListSerializer

logger = logging.getLogger('django')


def is_option(watchlist):
    return _is_option(watchlist.asset_type)

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

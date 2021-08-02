import logging
from datetime import datetime, timedelta
from brCore.models import WatchList
from common.types.asset_types import AssetTypes

logger = logging.getLogger('django')


def is_option(watchlist):
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value or watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        return True
    return False

def get_watchlist(asset_type, ticker, option_strike, option_expiry):
    watchlist = WatchList.objects.get(asset_type=asset_type,
                    ticker=ticker,
                    option_strike=option_strike,
                    option_expiry=option_expiry)
    return watchlist

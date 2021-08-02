import logging
from datetime import datetime, timedelta
from brCore.models import ScanEntry
from brSetting.models import Configuration
from common.types.asset_types import AssetTypes, TransactionType
from common.types.scan_types import ScanProfile

logger = logging.getLogger('django')

_scan_profile_for_call_option_lut = {
    TransactionType.BUY.value: ScanProfile.BUY_CALL.value,
    TransactionType.SELL.value: ScanProfile.SELL_CALL.value,
}

_scan_profile_for_put_option_lut = {
    TransactionType.BUY.value: ScanProfile.BUY_PUT.value,
    TransactionType.SELL.value: ScanProfile.SELL_PUT.value,
}


def create_if_not_exists(watchlist, entry_price, transaction_type):
    try:
        scan_entry = ScanEntry.objects.get(watchlist_id=int(watchlist.id))
        # Scan entry exists, return it
        return scan_entry
    except ScanEntry.DoesNotExist:
        #Scan entry does not exist. Add a scan entry
        logger.info('create_if_not_exists: ScanEntry not found for watchlist_id {}'.format(
            watchlist.id))

    # Need to Create a scan entry

    # When we sell,
    # 1. profit target should be less than entry_price
    # 2. stop loss should be more than entry_price
    configuration = Configuration.objects.first()

    profit_target = entry_price * \
        (100-configuration.profitTargetPercent)/100
    stop_loss = entry_price * \
        (100+configuration.stopLossPercent)/100

    scan_entry = ScanEntry(watchlist_id=watchlist.id,
                            profile=_get_scan_profile(watchlist, transaction_type),
                            profit_target=round(profit_target, 2),
                            stop_loss=round(stop_loss, 2))

    scan_entry.save()
    return scan_entry


def _get_scan_profile(watchlist, transaction_type):
    if watchlist.asset_type == AssetTypes.STOCK.value:
        return ScanProfile.BUY_STOCK.value

    if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
        return _scan_profile_for_put_option_lut[transaction_type]

    # Else its call option
    return _scan_profile_for_call_option_lut[transaction_type]
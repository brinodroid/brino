import threading
from brCore.models import BGTask, WatchList, PortFolio, ScanEntry
from brCore.types.bgtask_types import BGTaskAction, BGTaskStatus, BGTaskDataIdType
import time
import brine
import brifz
import logging
import sys
from datetime import datetime, timedelta
from .base import base_action
from brCore.types.scan_types import ScanStatus
from brCore.types.asset_types import AssetTypes

logger = logging.getLogger('django')


def __bgtask_get_portfolio(bgtask):
    if bgtask.dataIdType != BGTaskDataIdType.PORTFOLIO.value:
        logger.error('__bgtask_get_portfolio: Not portFolio dataId %s', bgtask)
        return None

    # May throw exceptions which will be caught at top level run thread
    portfolio = PortFolio.objects.get(pk=bgtask.dataId)
    return portfolio


def __bgtask_get_watchlist(bgtask, portfolio):
    watchListId = bgtask.dataId
    if bgtask.dataIdType == BGTaskDataIdType.PORTFOLIO.value:
        assert (portfolio)
        watchListId = portfolio.watchListId

    try:
        watchlist = WatchList.objects.get(pk=watchListId)
        return watchlist
    except WatchList.DoesNotExist:
        logger.error('__bgtask_get_watchlist: WatchList not found %d', watchListId)
        return None;


def __bgtask_stop(bgtask, status):
    bgtask.status = status
    bgtask.action = BGTaskAction.NONE.value;
    bgtask.save()


# TODO: At application start, we need to run all INPROGRESS tasks
def __bgtask_runner(bgtask_id):
    # TODO: Find a good place for login
    brine.login()
    while True:
        try:
            bgtask = BGTask.objects.get(pk=bgtask_id)
        except BGTask.DoesNotExist:
            logger.error('__bgtask_runner: stopping bgtask as task not found bgtask_id: %d', bgtask_id)
            return

        if bgtask.action == BGTaskAction.NONE.value:
            logger.info('__bgtask_runner: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            # Reset the status
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        if bgtask.status != BGTaskStatus.RUNNING.value:
            logger.info('__bgtask_runner: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        try:
            portfolio = __bgtask_get_portfolio(bgtask)
            if portfolio is None:
                logger.info('__bgtask_runner: Is not portfolio %s', bgtask)

            watchList = __bgtask_get_watchlist(bgtask, portfolio)
            if watchList is None:
                logger.error('__bgtask_runner: Cannot get watchList portfolio=%s bgtask=%s', portfolio, bgtask)
                __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
                return

            logger.info(bgtask)
            logger.info(portfolio)
            logger.info(watchList)
            base_action(bgtask, watchList, portfolio)

        except BaseException as error:
            # Catch all exceptions
            __bgtask_stop(bgtask, BGTaskStatus.FAIL.value)
            e = sys.exc_info()[0]
            logger.error("__bgtask_runner: caught  exception %s", error)

            # Stop the thread
            return;

        # Save the values
        bgtask.save()
        # Repeat the loop after 1min
        time.sleep(60)


def addScanATTNDetails(scan_entry, new_detail):
    if scan_entry.details:
        scan_entry.details += ' +++ '
    else:
        scan_entry.details = ' +++ '

    logger.info('__bgtask_scanner: adding making str scan_entry.details=%s, new details=%s',
                scan_entry.details, new_detail)
    scan_entry.details += new_detail
    scan_entry.status = ScanStatus.ATTN.value
    logger.info('__bgtask_scanner: added scan_entry.details=%s', scan_entry.details)
    return scan_entry


def __bgtask_scanner():
    brine.login()
    while True:
        try:
            scan_list = ScanEntry.objects.all()
        except ScanEntry.DoesNotExist:
            logger.info('__bgtask_scanner: No scan entries, check after 60s')
            time.sleep(60)
            continue

        for scan_entry in scan_list:
            # Rereading from DB to get the latest value
            scan_entry = ScanEntry.objects.get(pk=scan_entry.id)
            logger.info('__bgtask_scanner: checking %s', scan_entry)
            try:
                watchlist = WatchList.objects.get(pk=scan_entry.watchListId)
            except WatchList.DoesNotExist:
                logger.error('__bgtask_scanner: WatchList not found %d', scan_entry.watchListId)
                continue

            scan_entry.details = ""
            scan_entry.status = ScanStatus.NONE.value

            stock_price = brine.get_latest_price(watchlist.ticker, includeExtendedHours=True)
            stock_price_extended_hours_f = float(stock_price[0])
            if watchlist.assetType == AssetTypes.CALL_OPTION.value \
                    or watchlist.assetType == AssetTypes.PUT_OPTION.value:
                logger.info('__bgtask_scanner: get option price. watchlist=%s', watchlist)

                optionType = 'call'
                if watchlist.assetType == AssetTypes.PUT_OPTION.value:
                    optionType = 'put'

                option_raw_data = brine.options.get_option_market_data(watchlist.ticker,
                                                                       str(watchlist.optionExpiry),
                                                                       str(watchlist.optionStrike), 'call')
                option_data = option_raw_data[0][0]
                optionDetails = 'high={}, low={}, volume={}.'.format(option_data['high_price'],
                                                                     option_data['low_price'],
                                                                     option_data['volume'])
                mark_price = float(option_data['mark_price'])
                low_price = float(option_data['low_price'])
                high_price = float(option_data['high_price'])
                scan_entry.volatility = option_data['implied_volatility']
                scan_entry.shortfloat = 0
                scan_entry.currentPrice = mark_price
                scan_entry.details = optionDetails
                time_to_expiry = watchlist.optionExpiry - datetime.now().date()
                if time_to_expiry.days <= 10:
                    addScanATTNDetails(scan_entry, 'Expiry less than 10 days. Sell?')

                if watchlist.optionStrike < stock_price_extended_hours_f:
                    addScanATTNDetails(scan_entry, 'Stock price {} above strike price of {}.'.format(
                        stock_price_extended_hours_f, watchlist.optionStrike))
                elif abs(watchlist.optionStrike - stock_price_extended_hours_f) <= stock_price_extended_hours_f*5/100:
                    # 5% of strike price
                    addScanATTNDetails(scan_entry, 'Stock price {} within 5% of strike price {}.'.format(
                        stock_price_extended_hours_f, watchlist.optionStrike))

                if mark_price >= scan_entry.resistance:
                    addScanATTNDetails(scan_entry, 'Near resistance. Sell?')
                elif mark_price <= scan_entry.support:
                    addScanATTNDetails(scan_entry, 'Near support target. Buy?')

                if high_price > scan_entry.resistance:
                    addScanATTNDetails(scan_entry, 'Update resistance?')

                if low_price < scan_entry.support:
                    addScanATTNDetails(scan_entry, 'Update support?')

            else:
                brifz_stats = brifz.get_stock(watchlist.ticker)
                brifz_target_price = float(brifz_stats['Target Price'])
                stock_price = brine.get_latest_price(watchlist.ticker)
                stock_price_regular_hours_f = float(stock_price[0])

                if stock_price_extended_hours_f >= scan_entry.resistance:
                    addScanATTNDetails(scan_entry, 'Near resistance. Sell?')
                elif stock_price_extended_hours_f <= scan_entry.support:
                    addScanATTNDetails(scan_entry, 'Near support target. Buy?')

                if abs(stock_price_extended_hours_f - stock_price_regular_hours_f) > stock_price_regular_hours_f * 1 / 100:
                    # Change in price more than 1% during after hours
                    addScanATTNDetails(scan_entry,
                                   '1% change in price during extended hours. regular price={}'
                                   .format(stock_price_regular_hours_f))
                if scan_entry.fvTargetPrice != brifz_target_price:
                    addScanATTNDetails(scan_entry,
                                   'fvTargetPrice updated to {} from {}'.format(brifz_target_price,
                                                                                scan_entry.fvTargetPrice))

                scan_entry.volatility = brifz_stats['Volatility']
                scan_entry.shortfloat = brifz_stats['Short Float']
                scan_entry.currentPrice = stock_price_extended_hours_f

            logger.info('__bgtask_scanner: Updating %s', scan_entry)
            scan_entry.save()

        time.sleep(60)


def __bgtask_thread_start(bgtask):
    t = threading.Thread(target=__bgtask_runner,
                         args=[bgtask.id])
    t.setDaemon(True)
    # Mark the task as running before starting thread
    logger.info('Starting thread for %s', bgtask)
    bgtask.status = BGTaskStatus.RUNNING.value;
    bgtask.save()
    t.start()


def start_bgtask(bgtask):
    if bgtask.status != BGTaskAction.NONE.value:
        logger.info('Starting bgtask: %s', bgtask)
        __bgtask_thread_start(bgtask)
    return bgtask


def start_bgscan():
    t = threading.Thread(target=__bgtask_scanner,
                         args=[])
    t.setDaemon(True)
    # Mark the task as running before starting thread
    logger.info('Starting scanner thread')
    t.start()

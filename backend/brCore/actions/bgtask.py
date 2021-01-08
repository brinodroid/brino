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
from brCore.types.scan_types import ScanStatus, ScanProfile
from brCore.types.asset_types import AssetTypes
import requests

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

def __float_string_convert(float_string):
    try:
        f = float(float_string)
        return f
    except:
        logger.info('__float_sting_convert: Not valid number =%s', float_string)
    return None


def __addAlertDetails(scan_cache, new_detail):
    scan_cache['details'] += ' +++ '
    scan_cache['details'] += new_detail
    scan_cache['status'] = ScanStatus.ATTN.value
    logger.info('__bgtask_scanner: added scan_cache=%s', scan_cache)

def __scan_support_resistance_alert(scan_entry, watchlist, scan_cache):
    if scan_cache['current_price'] >= scan_entry.resistance:
        __addAlertDetails(scan_cache, 'Near resistance. Sell?')
    elif scan_cache['current_price'] <= scan_entry.support:
        __addAlertDetails(scan_cache, 'Near support target. Buy?')

def __scan_extended_hours_price_movement_alert(scan_entry, watchlist, scan_cache):
    #get regular hours price
    stock_price = brine.get_latest_price(watchlist.ticker, includeExtendedHours=False)
    stock_price_regular_hours_f = float(stock_price[0])

    if abs(scan_cache['current_price'] - stock_price_regular_hours_f) > stock_price_regular_hours_f * 1 / 100:
        # Change in price more than 1% during after hours
        __addAlertDetails(scan_cache,
                          '1% change in price during extended hours. regular price={}'
                          .format(stock_price_regular_hours_f))

def __scan_brifz_target_price_update_alert(scan_entry, watchlist, scan_cache):
    if scan_cache['brifz_target_price'] is not None and scan_cache['brifz_target_price'] != scan_entry.fvTargetPrice:
            __addAlertDetails(scan_cache,
                          'fvTargetPrice updated to {} from {}'.format(scan_cache['brifz_target_price'],
                                                                       scan_entry.fvTargetPrice))

def __scan_option_time_to_expiry_alert(scan_entry, watchlist, scan_cache):
    time_to_expiry = watchlist.optionExpiry - datetime.now().date()
    if time_to_expiry.days <= 10:
        __addAlertDetails(scan_cache, 'Expiry less than 10 days. Sell?')


def __scan_option_strike_alert(scan_entry, watchlist, scan_cache):
    if watchlist.optionStrike < scan_cache['stock_price']:
        __addAlertDetails(scan_cache, 'Stock price {} above strike price of {}.'.format(
            scan_cache['stock_price'], watchlist.optionStrike))
    elif abs(watchlist.optionStrike - scan_cache['stock_price']) <= scan_cache['stock_price'] * 5 / 100:
        # 5% of strike price
        __addAlertDetails(scan_cache, 'Stock price {} within 5% of strike price {}.'.format(
            scan_cache['stock_price'], watchlist.optionStrike))

def __scan_support_resistance_update_alert(scan_entry, watchlist, scan_cache):
    if scan_cache['high_price'] is not None and scan_cache['high_price'] > scan_entry.resistance:
        __addAlertDetails(scan_cache, 'Update resistance?')

    if scan_cache['low_price'] is not None and scan_cache['low_price'] < scan_entry.support:
        __addAlertDetails(scan_cache, 'Update support?')

def __scan_covered_call_price_alert(scan_entry, watchlist, scan_cache):
    if scan_cache['current_price'] < scan_entry.profitTarget*10/100:
        __addAlertDetails(scan_cache, 'Current price is less than 10% of profit target. Buy back and sell CC again?')

    if scan_cache['current_price'] > scan_entry.profitTarget*80/100:
        #Price reached 80% of profit target.
        __addAlertDetails(scan_cache, 'Current price went beyond 80% of profit target. Buy back and sell CC again?')

scan_checks = {
    ScanProfile.STOCK.value:
        [__scan_support_resistance_alert, __scan_extended_hours_price_movement_alert,
            __scan_brifz_target_price_update_alert],
    ScanProfile.CC.value:
        [__scan_support_resistance_alert, __scan_option_time_to_expiry_alert, __scan_option_strike_alert,
            __scan_support_resistance_update_alert, __scan_covered_call_price_alert],
    ScanProfile.CALL.value:
        [__scan_support_resistance_alert, __scan_option_time_to_expiry_alert,
            __scan_support_resistance_update_alert],
    ScanProfile.PUT.value:
        [__scan_support_resistance_alert, __scan_option_time_to_expiry_alert,
            __scan_support_resistance_update_alert],
}

def __bgtask_scanner():
    brine.login()
    while True:
        try:
            scan_list = ScanEntry.objects.all()
        except ScanEntry.DoesNotExist:
            logger.info('__bgtask_scanner: No scan entries, check after 60s')
            time.sleep(120)
            continue

        for scan_entry in scan_list:
            logger.info('__bgtask_scanner: checking %s', scan_entry)
            try:
                watchlist = WatchList.objects.get(pk=scan_entry.watchListId)
            except WatchList.DoesNotExist:
                logger.error('__bgtask_scanner: WatchList not found %d', scan_entry.watchListId)
                continue

            try:
                stock_price = brine.get_latest_price(watchlist.ticker, includeExtendedHours=True)
            except requests.exceptions.ConnectionError:
                logger.error('__bgtask_scanner: Connection error for %d. Wait and continue', scan_entry.watchListId)
                time.sleep(120)
                logger.info('__bgtask_scanner: Retrying after connection error', scan_entry.watchListId)
                continue

            scan_cache = {}
            scan_cache['stock_price'] = float(stock_price[0])
            scan_cache['details'] = ""
            scan_cache['status'] = ScanStatus.NONE.value

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
                scan_cache['details'] = 'high={}, low={}, volume={}.'.format(option_data['high_price'],
                                                                     option_data['low_price'],
                                                                     option_data['volume'])
                scan_cache['current_price'] = __float_string_convert(option_data['mark_price'])
                scan_cache['low_price'] = __float_string_convert(option_data['low_price'])
                scan_cache['high_price'] = __float_string_convert(option_data['high_price'])
                scan_cache['volatility'] = __float_string_convert(option_data['implied_volatility'])
                scan_cache['shortfloat'] = 0
                scan_cache['brifz_target_price'] = 0

            else:
                #Stocks
                brifz_stats = brifz.get_stock(watchlist.ticker)

                scan_cache['current_price'] = scan_cache['stock_price']
                scan_cache['low_price'] = 0
                scan_cache['high_price'] = 0
                scan_cache['volatility'] = brifz_stats['Volatility']
                scan_cache['shortfloat'] = brifz_stats['Short Float']
                scan_cache['brifz_target_price'] = __float_string_convert(brifz_stats['Target Price'])

            #Call all scan_checks of the given profile
            for scan_check in scan_checks[scan_entry.profile]:
                scan_check(scan_entry, watchlist, scan_cache)

            # Rereading from DB to get the latest value. TODO: Need locking
            scan_entry = ScanEntry.objects.get(pk=scan_entry.id)
            scan_entry.details = scan_cache['details']
            scan_entry.status = scan_cache['status']
            scan_entry.currentPrice = scan_cache['current_price']
            scan_entry.volatility = scan_cache['volatility']
            scan_entry.shortfloat = scan_cache['shortfloat']
            scan_entry.save()
            logger.info('__bgtask_scanner: Updated {} from cache {}'.format(scan_entry, scan_cache))

        time.sleep(120)


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

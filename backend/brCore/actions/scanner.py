import threading
import time
import logging
from datetime import datetime, timedelta
import brifz
from brCore.models import WatchList, ScanEntry
from brCore.client.Factory import get_client
from brCore.types.scan_types import ScanStatus, ScanProfile
from brCore.types.asset_types import AssetTypes

logger = logging.getLogger('django')


class Scanner:
    __instance = None
    __sleep_duration = 60

    __SCAN_ERROR_MSG = 'ERROR'
    __SCAN_WARN_MSG = 'WARNING'
    __SCAN_INFO_MSG = 'INFO'

    __SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY = 'latest_ticker_price_dict'
    __SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY = 'market_hours_ticker_price_dict'
    __SCAN_DATA_BRIFZ_STAT_DICT_KEY = 'brifz_stats_dict'
    __SCAN_DATA_LOCAL_OPTION_DATA_KEY = 'local_option_data'

    def __init__(self):
        """ Virtually private constructor. """
        if Scanner.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Scanner.__instance = self

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Scanner.__instance == None:
            Scanner()
        return Scanner.__instance

    def start(self):
        t = threading.Thread(target=self.__scanner_thread, args=[])
        t.setDaemon(True)
        # Mark the task as running before starting thread
        logger.info('Starting scanner thread')
        t.start()

    def __scanner_thread(self):
        # Get the default client
        client = get_client()

        while True:
            try:
                scan_list = ScanEntry.objects.all()
            except ScanEntry.DoesNotExist:
                # Nothing to scan
                logger.info('__scanner_thread: No scan entries, check after {}'.format(
                    self.__sleep_duration))
                time.sleep(self.__sleep_duration)
                continue

            uniq_ticker_list = self.__get_uniq_ticker_list(scan_list)
            latest_ticker_price_dict = client.get_ticker_price_dict(
                uniq_ticker_list, True)
            market_hours_ticker_price_dict = client.get_ticker_price_dict(
                uniq_ticker_list, False)

            brifz_stats_dict = self.__get_brifz_stats_dict(uniq_ticker_list)

            if latest_ticker_price_dict is None and brifz_stats_dict is None:
                # Cannot get the latest price from client. Sleep and try again
                logger.error('__scanner_thread: Failed to get the latest info. Try again after {}'
                             .format(self.__sleep_duration))

                time.sleep(self.__sleep_duration)
                continue

            scan_data = {}
            scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY] = latest_ticker_price_dict
            scan_data[self.__SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY] = market_hours_ticker_price_dict
            scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY] = brifz_stats_dict

            for scan_entry in scan_list:
                logger.info('__scanner_thread: checking {}'.format(scan_entry))

                # Resetting the values
                scan_entry.details = ""
                scan_entry.status = ScanStatus.NONE.value

                self.__update_scan_entry_values(scan_entry, scan_data, client)

                self.__update_scan_entry_in_db(scan_entry)

            time.sleep(self.__sleep_duration)

    def __update_scan_entry_values(self, scan_entry, scan_data, client):
        try:
            watchlist = WatchList.objects.get(pk=scan_entry.watchlist_id)
        except WatchList.DoesNotExist:
            logger.error('__update_scan_data: WatchList not found {}'.format(
                scan_entry.watchlist_id))
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'Watchlist missing.')
            return

        if watchlist.asset_type == AssetTypes.CALL_OPTION.value \
                or watchlist.asset_type == AssetTypes.PUT_OPTION.value:

            optionType = 'call'
            if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
                optionType = 'put'

            # TODO: get_option_price can return a list of option prices?
            option_raw_data = client.get_option_price(watchlist.ticker,
                                                      str(watchlist.option_expiry),
                                                      str(watchlist.option_strike), optionType)
            option_data = option_raw_data[0][0]
            scan_data[self.__SCAN_DATA_LOCAL_OPTION_DATA_KEY] = option_data

            scan_entry.details = 'high={}, low={}, volume={}.'.format(option_data['high_price'],
                                                                      option_data['low_price'],
                                                                      option_data['volume'])
            scan_entry.current_price = self.__safe_float(
                option_data['mark_price'])
            scan_entry.volatility = self.__safe_float(
                option_data['implied_volatility'])
            scan_entry.short_float = 0

        else:
            # Update  current price, volatility and short float
            scan_entry.current_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]
            scan_entry.volatility = self.__get_brifz_volatility(
                scan_entry, watchlist, scan_data)
            scan_entry.short_float = self.__get_brifz_shortfloat(
                scan_entry, watchlist, scan_data)
            scan_entry.brifz_target = self.__get_brifz_target(
                scan_entry, watchlist, scan_data)

        # Call all __scan_profile_check of the given profile
        for scan_profile_check in self.__scan_profile_check_list[scan_entry.profile]:
            try:
                scan_profile_check(self, scan_entry, watchlist, scan_data)
            except Exception as e:
                logger.error(
                    '__update_scan_entry_values: scan_profile_check: {} gave Exception: {}'.format(scan_profile_check, repr(e)))
                self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                       'scan_profile_check: {} gave Exception: {}'.format(scan_profile_check, repr(e)))

        # Reset the option data to not use stale info
        scan_data[self.__SCAN_DATA_LOCAL_OPTION_DATA_KEY] = None

    def __get_brifz_volatility(self, scan_entry, watchlist, scan_data):
        try:
            return self.__safe_float(scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY][watchlist.ticker]['Volatility'])
        except Exception as e:
            logger.error(
                '__get_brifz_volatility: Exception: {}'.format(repr(e)))
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, '__get_brifz_volatility: Exception: {}'.format(repr(e)))
        return None

    def __get_brifz_shortfloat(self, scan_entry, watchlist, scan_data):
        try:
            return self.__safe_float(scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY][watchlist.ticker]['Short Float'])
        except Exception as e:
            logger.error(
                '__get_brifz_shortfloat: Exception: {}'.format(repr(e)))
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, '__get_brifz_shortfloat: Exception: {}'.format(repr(e)))
        return None

    def __get_brifz_target(self, scan_entry, watchlist, scan_data):
        try:
            return self.__safe_float(scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY][watchlist.ticker]['Target Price'])
        except Exception as e:
            logger.error(
                '__get_brifz_target: Exception: {}'.format(repr(e)))
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, '__get_brifz_target: Exception: {}'.format(repr(e)))
        return None

    def __get_uniq_ticker_list(self, scan_list):
        ticker_list = []

        for scan_entry in scan_list:
            logger.info(
                '__get_uniq_ticker_list: checking {}'.format(scan_entry))
            try:
                watchlist = WatchList.objects.get(pk=scan_entry.watchlist_id)
            except WatchList.DoesNotExist:
                logger.error('__get_uniq_ticker_list: WatchList not found {}'.format(
                    scan_entry.watchlist_id))
                continue

            # Append to the ticker list if does not already exists
            if watchlist.ticker not in ticker_list:
                ticker_list.append(watchlist.ticker)

        return ticker_list

    def __get_brifz_stats_dict(self, uniq_ticker_list):
        try:
            ticker_brifz_static_dict = {}
            for ticker in uniq_ticker_list:
                brifz_stats = brifz.get_stock(ticker)
                ticker_brifz_static_dict[ticker] = brifz_stats

            return ticker_brifz_static_dict
        except Exception as e:
            logger.error(
                '__get_brifz_stats_dict: Exception: {}'.format(repr(e)))
            return None

    def __safe_float(self, float_string):
        try:
            f = float(float_string)
            return f
        except:
            logger.info('__safe_float: Not valid number =%s', float_string)
        return None

    def __addAlertDetails(self, scan_entry, level, new_detail):
        scan_entry.details += '--> {}: {}'.format(level, new_detail)
        scan_entry.status = ScanStatus.ATTN.value
        logger.info('__addAlertDetails: added scan_entry=%s', scan_entry)

    def __update_scan_entry_in_db(self, scan_entry):
        # Rereading from DB to get the latest value. TODO: Need locking with API updates
        scan_latest_entry = ScanEntry.objects.get(pk=scan_entry.id)
        scan_latest_entry.details = scan_entry.details
        scan_latest_entry.status = scan_entry.status
        scan_latest_entry.current_price = scan_entry.current_price
        scan_latest_entry.volatility = scan_entry.volatility
        scan_latest_entry.short_float = scan_entry.short_float
        scan_latest_entry.save()
        logger.info('__update_scan_entry_in_db: Updated {} with {}'.format(
            scan_latest_entry, scan_entry))

    def __check_support_resistance_alert(self, scan_entry, watchlist, scan_data):
        # current_price contains the latest price for option or stock
        latest_price = scan_entry.current_price

        if scan_entry.resistance is None or scan_entry.resistance == 0:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'Resistance data missing.')
        elif scan_entry.resistance <= latest_price:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_WARN_MSG, 'Hitting resistance. Sell?')

        if scan_entry.support is None or scan_entry.support == 0:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'Support data missing.')
        elif scan_entry.support >= latest_price:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_WARN_MSG, 'Hitting support. Buy?')

    def __check_extended_hours_price_movement_alert(self, scan_entry, watchlist, scan_data):
        latest_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]
        market_hours_price = scan_data[self.__SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY][watchlist.ticker]

        if abs(latest_price - market_hours_price) >= market_hours_price * 1 / 100:
            # Change in price more than 1% during after hours
            self.__addAlertDetails(scan_entry, self.__SCAN_WARN_MSG,
                                   '1% change in price during extended hours. regular price={}'
                                   .format(market_hours_price))

    def __check_brifz_target_price_update_alert(self, scan_entry, watchlist, scan_data):
        if scan_entry.brifz_target is None or scan_entry.brifz_target == 0:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'Brifz target missing.')
            return

        latest_brifz_target = scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY][watchlist.ticker]

        if scan_entry.brifz_target != latest_brifz_target:
            # Update in brifz target price
            self.__addAlertDetails(scan_entry, self.__SCAN_WARN_MSG,
                                   'brifz_target updated to {} from {}'
                                   .format(latest_brifz_target, scan_entry.brifz_target))

    def __check_option_time_to_expiry_alert(self, scan_entry, watchlist, scan_data):
        time_to_expiry = watchlist.option_expiry - datetime.now().date()
        if time_to_expiry.days <= 10:
            self.__addAlertDetails(scan_entry, self.__SCAN_WARN_MSG,
                                   'Expiry less than 10 days. Close?')

        if time_to_expiry.days <= 5:
            self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                   'Expiry less than 5 days. Close?')

    def __check_option_strike_alert(self, scan_entry, watchlist, scan_data):
        latest_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]

        if watchlist.option_strike < latest_price:
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Stock price {} above strike price of {}.'
                                   .format(latest_price, watchlist.option_strike))

        elif abs(watchlist.option_strike - latest_price) <= latest_price * 5 / 100:
            # 5% of strike price
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Stock price {} within 5% strike price of {}.'
                                   .format(latest_price, watchlist.option_strike))

    def __check_sold_option_buyback_alert(self, scan_entry, watchlist, scan_data):
        if scan_entry.profit_target is None or scan_entry.profit_target == 0:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'profit_target data missing.')
            return

        latest_option_price = scan_entry.current_price

        if latest_option_price < scan_entry.profit_target*10/100:
            self.__addAlertDetails(scan_entry, self.__SCAN_WARN_MSG,
                                   'Current price is less than 10% of profit target. Buy back and sell CC again?')

        if latest_option_price > scan_entry.profit_target*80/100:
            # Price reached 80% of profit target.
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Current price went beyond 80% of profit target. Buy back and sell CC again?')

    __scan_profile_check_list = {
        ScanProfile.BUY_STOCK.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_brifz_target_price_update_alert
            ],
        ScanProfile.SELL_CALL.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_strike_alert,
                __check_option_time_to_expiry_alert,
                __check_sold_option_buyback_alert
            ],
        ScanProfile.BUY_CALL.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_strike_alert,
                __check_option_time_to_expiry_alert,
            ],
        ScanProfile.BUY_PUT.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_strike_alert,
                __check_option_time_to_expiry_alert,
            ],
        ScanProfile.SELL_PUT.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_strike_alert,
                __check_option_time_to_expiry_alert,
                __check_sold_option_buyback_alert
            ],
    }

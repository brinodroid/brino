import threading
import time
import logging
import sys
from datetime import datetime, timedelta
import brifz
from django.db.models import Q
from common.client.Factory import get_client
from common.types.scan_types import ScanStatus, ScanProfile
from common.types.asset_types import AssetTypes, TransactionType

from brCore.models import WatchList, ScanEntry, PortFolio
from brOrder.models import OpenOrder
from common.actions.strategy import Strategy
import common.utils as utils

logger = logging.getLogger('django')


class Scanner:
    __instance = None
    #5min sleep
    __sleep_duration = 60

    __SCAN_ERROR_MSG = 'ERROR'
    __SCAN_WARN_MSG = 'WARNING'
    __SCAN_INFO_MSG = 'INFO'

    __SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY = 'latest_ticker_price_dict'
    __SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY = 'market_hours_ticker_price_dict'
    __SCAN_DATA_BRIFZ_STAT_DICT_KEY = 'brifz_stats_dict'
    __SCAN_DATA_LOCAL_OPTION_DATA_KEY = 'local_option_data'
    __lock = threading.Lock()

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

    def get_lock(self):
        return self.__lock

    def __scanner_run_with_lock(self, client):
        try:
            scan_list = ScanEntry.objects.filter(
                ~Q(status=ScanStatus.MISSING.value))
        except ScanEntry.DoesNotExist:
            # Nothing to scan
            logger.info('__scanner_thread: No scan entries, check after {}'.format(
                self.__sleep_duration))
            return

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
            return

        scan_data = {}
        scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY] = latest_ticker_price_dict
        scan_data[self.__SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY] = market_hours_ticker_price_dict
        scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY] = brifz_stats_dict

        for scan_entry in scan_list:

            logger.info(
                '__scanner_thread: running scanner for {}'.format(scan_entry))

            # Resetting the values
            scan_entry.details = ""
            scan_entry.status = ScanStatus.NONE.value

            self.__process_scan_entry_values(scan_entry, scan_data, client)

            self.__update_scan_entry_in_db(scan_entry)

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

            self.__lock.acquire()
            try:
                self.__scanner_run_with_lock(client)
            finally:
                self.__lock.release()

            time.sleep(self.__sleep_duration)

    def scan(self):
        # Get the default client
        client = get_client()

        self.__scanner_run_with_lock(client)
        return


    def __get_closest_strike_above_price(self, option_list, price):
        min=sys.float_info.max
        closest_option = None
        for option in option_list:
            if option is None:
                logger.error(
                    '__get_closest_strike_above_price: option {} looks is None'
                    .format(option))
                continue

            if 'strike_price' not in option:
                logger.error(
                    '__get_closest_strike_above_price: option {} looks invalid'
                    .format(option))
                continue

            strike_price = utils.safe_float(option['strike_price'])
            if strike_price == None:
                logger.error(
                    '__get_closest_strike_above_price: option {} looks invalid'
                    .format(option))
                continue

            if price >= strike_price:
                # the strike price is lower, skip it
                continue

            # Strike price is more than the latest_price
            if min > (strike_price - price):
                min = strike_price - price
                closest_option = option
        return closest_option

    def __get_closest_strike_below_price(self, option_list, price):
        min=sys.float_info.max
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
                min = price - strike_price
                closest_option = option
        return closest_option

    def __compute_monthly_call_iv(self, scan_entry, watchlist, client):
        # current_price contains the latest price for option or stock
        latest_price = scan_entry.current_price

        # Get call option monthly expiry date after 20days beyond current date.
        next_monthly_expiry = utils.third_friday_of_next_month()

        # Get call option strike price at 5 levels beyond latest price
        options_list = client.get_all_options_on_expiry_date(watchlist.ticker, next_monthly_expiry, 'call')
        if options_list == None:
            logger.error(
                '__compute_monthly_call_iv: get_all_options_on_expiry_date() for watchlist.id {} didnt get any data'
                .format(watchlist.id))
            return None

        closest_option = self.__get_closest_strike_above_price(options_list, latest_price)
        if closest_option == None:
            logger.error(
                '__compute_monthly_call_iv: __get_closest_strike_above_price() for watchlist.id {} didnt get any data'
                .format(watchlist.id))
            return None

        option_raw_data = client.get_option_price(watchlist.ticker,
                                next_monthly_expiry.strftime(utils.option_expiry_date_strpfmt_string),
                                closest_option['strike_price'], 'call')

        # Sometimes option data seems empty
        if len(option_raw_data) == 0 or len(option_raw_data[0]) == 0:
            logger.error(
                '__compute_monthly_call_iv: get_option_price() for watchlist.id {} didnt get any data'
                .format(watchlist.id))
            return None

        option_data = option_raw_data[0][0]

        # Get the iv and updadte it
        return round(utils.safe_float(option_data['implied_volatility'])*100, 2)

    def __compute_monthly_put_iv(self, scan_entry, watchlist, client):
        # current_price contains the latest price for option or stock
        latest_price = scan_entry.current_price

        # Get call option monthly expiry date after 20days beyond current date.
        next_monthly_expiry = utils.third_friday_of_next_month()

        # Get call option strike price at 5 levels beyond latest price
        options_list = client.get_all_options_on_expiry_date(watchlist.ticker, next_monthly_expiry, 'put')
        if options_list == None:
            logger.error(
                '__compute_monthly_put_iv: get_all_options_on_expiry_date() for watchlist.id {} didnt get any data'
                .format(watchlist.id))
            return None

        closest_option = self.__get_closest_strike_below_price(options_list, latest_price)
        if closest_option == None:
            logger.error(
                '__compute_monthly_put_iv: get_all_options_on_expiry_date() for watchlist.id {} didnt get any data'
                .format(watchlist.id))
            return None

        option_raw_data = client.get_option_price(watchlist.ticker,
                                next_monthly_expiry.strftime(utils.option_expiry_date_strpfmt_string),
                                closest_option['strike_price'], 'put')

        # Sometimes option data seems empty
        if len(option_raw_data) == 0 or len(option_raw_data[0]) == 0:
            logger.error(
                '__compute_monthly_put_iv: get_option_price() for watchlist.id {} didnt get any data'
                .format(watchlist.id))
            return None

        option_data = option_raw_data[0][0]

        # Get the iv and updadte it
        return round(utils.safe_float(option_data['implied_volatility'])*100, 2)



    def __compute_reward_2_risk(self, scan_entry):
        if scan_entry.support is None:
            #Some options may not have support price
            return None

        # current_price contains the latest price for option or stock

        latest_price = scan_entry.current_price
        risk = latest_price - scan_entry.support
        reward = scan_entry.resistance - latest_price
        if risk == 0:
            risk = 0.001

        return round(reward/risk, 2)

    def __compute_potential(self, scan_entry):
        target = scan_entry.brifz_target
        if target is None:
            if scan_entry.brate_target is None:
                #Cannot compute the potential
                return None

            #We have brate target, use it
            target = scan_entry.brate_target

        if scan_entry.current_price == 0:
            # Avoid division by 0
            potential = 0
        else:
            potential = target/scan_entry.current_price
        return round(potential, 2)

    def __process_scan_entry_values(self, scan_entry, scan_data, client):
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

            now = datetime.now().date()
            time_to_expiry = watchlist.option_expiry - datetime.now().date()

            if now > watchlist.option_expiry:
                # This option has expired. Brine cannot get market data on it
                self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                       'Option EXPIRED')
                return

            optionType = 'call'
            if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
                optionType = 'put'

            try:
                # TODO: get_option_price can return a list of option prices?
                option_raw_data = client.get_option_price(watchlist.ticker,
                                                          str(watchlist.option_expiry),
                                                          str(watchlist.option_strike), optionType)

                # Sometimes option data seems empty
                if len(option_raw_data) == 0 or len(option_raw_data[0]) == 0:
                    logger.error(
                        '__update_scan_entry_values: get_option_price() for watchlist.id {} didnt get any data'
                        .format(watchlist.id))
                    self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                           'get_option_price() failed to get ata for watchlist.id {} '.format(watchlist.id))
                    return

            except Exception as e:
                logger.error(
                    '__update_scan_entry_values: get_option_price() for watchlist.id {} gave Exception: {}'
                    .format(watchlist.id, repr(e)))
                self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                       'get_option_price() for watchlist.id {} gave Exception: {}'.format(watchlist.id, repr(e)))
                # Cannot process. Return
                return

            option_data = option_raw_data[0][0]
            scan_data[self.__SCAN_DATA_LOCAL_OPTION_DATA_KEY] = option_data

            scan_entry.details = 'high={}, low={}, volume={}.'.format(option_data['high_price'],
                                                                      option_data['low_price'],
                                                                      option_data['volume'])
            scan_entry.current_price = self.__safe_float(
                option_data['mark_price'])
            scan_entry.volatility = round(self.__safe_float(
                option_data['implied_volatility'])*100, 2)
            scan_entry.short_float = 0

        else:
            # Update  current price, volatility and short float
            if scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY] is not None:
                scan_entry.current_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]
            else:
                logger.error(
                    'Latest price for {} is unavailable'.format(watchlist.ticker))

            scan_entry.volatility = self.__get_brifz_volatility(
                scan_entry, watchlist, scan_data)
            scan_entry.short_float = self.__get_brifz_shortfloat(
                scan_entry, watchlist, scan_data)
            #if scan_entry.brifz_target is None:
            # Update brifz_target always as it will be noted in the history
            scan_entry.brifz_target = self.__get_brifz_target(
                    scan_entry, watchlist, scan_data)

            scan_entry.call_iv_next_month = self.__compute_monthly_call_iv(scan_entry, watchlist, client)
            scan_entry.put_iv_next_month = self.__compute_monthly_put_iv(scan_entry, watchlist, client)



        scan_entry.reward_2_risk = self.__compute_reward_2_risk(scan_entry)
        scan_entry.potential = self.__compute_potential(scan_entry)

        # Call all __scan_profile_check of the given profile
        for scan_profile_check in self.__scan_profile_check_list[scan_entry.profile]:
            try:
                scan_profile_check(self, scan_entry, watchlist, scan_data)
            except Exception as e:
                logger.error(
                    '__update_scan_entry_values: scan_profile_check: {} gave Exception: {}'.format(scan_profile_check, repr(e)))
                self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                       'scan_profile_check: {} gave Exception: {}'.format(scan_profile_check, repr(e)))

        # Run the strategy too
        Strategy.getInstance().run_strategy(scan_entry, watchlist, scan_data, client)

        # Reset the option data to not use stale info
        scan_data[self.__SCAN_DATA_LOCAL_OPTION_DATA_KEY] = None

    def __get_brifz_volatility(self, scan_entry, watchlist, scan_data):
        try:
            if scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY] is None:
                return "No data"

            # Else get the data
            return scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY][watchlist.ticker]['Volatility']
        except Exception as e:
            logger.error(
                '__get_brifz_volatility: Exception: {}'.format(repr(e)))
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, '__get_brifz_volatility: Exception: {}'.format(repr(e)))
        return None

    def __get_brifz_shortfloat(self, scan_entry, watchlist, scan_data):
        try:
            if scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY] is None:
                return "No data"

            # Else get the data
            return scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY][watchlist.ticker]['Short Float']
        except Exception as e:
            logger.error(
                '__get_brifz_shortfloat: Exception: {}'.format(repr(e)))
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, '__get_brifz_shortfloat: Exception: {}'.format(repr(e)))
        return None

    def __get_brifz_target(self, scan_entry, watchlist, scan_data):
        try:
            if scan_data[self.__SCAN_DATA_BRIFZ_STAT_DICT_KEY] is None:
                return "No data"

            # Else get the data
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
                brifz_stats = brifz.get_stock(ticker.replace('.', '-'))
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
        return 0

    def __addAlertDetails(self, scan_entry, level, new_detail):
        scan_entry.details += '--> {}: {}'.format(level, new_detail)
        if level != self.__SCAN_INFO_MSG:
            #Change the status to ATTN only if the message is either warnings or error
            scan_entry.status = ScanStatus.ATTN.value

        logger.info('__addAlertDetails: added scan_entry=%s', scan_entry)

    def __set_default_support_resistance(self, scan_entry):
        # Set default resistance as profit target

        if scan_entry.profile == ScanProfile.SELL_CALL.value \
                or scan_entry.profile == ScanProfile.SELL_PUT.value:
            # For sell transactions, we expect profit target to be lower than stop loss.
            if scan_entry.resistance is None or scan_entry.resistance == 0:
                scan_entry.resistance = scan_entry.stop_loss

            if scan_entry.support is None or scan_entry.support == 0:
                scan_entry.support = scan_entry.profit_target

        else:
            if scan_entry.resistance is None or scan_entry.resistance == 0:
                scan_entry.resistance = scan_entry.profit_target

            if scan_entry.support is None or scan_entry.support == 0:
                scan_entry.support = scan_entry.stop_loss

    def __update_scan_entry_in_db(self, scan_entry):
        # Rereading from DB to get the latest value. TODO: Need locking with API updates
        scan_latest_entry = ScanEntry.objects.get(pk=scan_entry.id)
        scan_latest_entry.details = scan_entry.details
        scan_latest_entry.status = scan_entry.status
        scan_latest_entry.current_price = scan_entry.current_price
        scan_latest_entry.volatility = scan_entry.volatility
        scan_latest_entry.short_float = scan_entry.short_float
        scan_latest_entry.reward_2_risk = scan_entry.reward_2_risk
        scan_latest_entry.potential = scan_entry.potential
        scan_latest_entry.active_track = scan_entry.active_track
        scan_latest_entry.order_id = scan_entry.order_id
        scan_latest_entry.put_iv_next_month = scan_entry.put_iv_next_month
        scan_latest_entry.call_iv_next_month = scan_entry.call_iv_next_month

        self.__set_default_support_resistance(scan_latest_entry)

        if (scan_latest_entry.brifz_target is None) or (scan_latest_entry.brifz_target != scan_entry.brifz_target):
            # Update brifz_target if not present. This is done to generate the UPGRADE/DOWNGRADE alerts
            scan_latest_entry.brifz_target = scan_entry.brifz_target

        scan_latest_entry.save()
        logger.info('__update_scan_entry_in_db: Updated {} with {}'.format(
            scan_latest_entry, scan_entry))

    def __check_missed_covered_call_sell_alert(self, scan_entry, watchlist, scan_data):
        # TODO: Find a way to restrict the check to a source to BRINE

        # Get a list of all watchlists with this ticker
        ticker_watchlist_list = WatchList.objects.filter(
            ticker=watchlist.ticker)

        total_sold_calls = 0
        total_bought_calls = 0
        total_stock_units = 0
        total_open_sell_orders=0

        for ticker_watchlist in ticker_watchlist_list:
            portfolio_list = PortFolio.objects.all().filter(
                watchlist_id=ticker_watchlist.id)
            for portfolio in portfolio_list:
                if ticker_watchlist.asset_type == AssetTypes.STOCK.value:
                    total_stock_units += portfolio.units
                elif ticker_watchlist.asset_type == AssetTypes.CALL_OPTION.value:
                    if portfolio.transaction_type == TransactionType.BUY.value:
                        total_bought_calls += portfolio.units
                    else:
                        total_sold_calls += portfolio.units

        # Get the list of watchlists with the ticker
        ticker_watchlist_id_list=[watchlist.id for watchlist in ticker_watchlist_list]

        open_orders_list = OpenOrder.objects.all()
        # Searching manually as the watchlist is kept as a comma seperated list of strings
        for open_order in open_orders_list:
            watchlist_id_list_in_order = open_order.watchlist_id_list.split(',')
            transaction_type_list_in_order = open_order.transaction_type_list.split(',')
            for (watchlist_id, transaction_type) in zip(watchlist_id_list_in_order, transaction_type_list_in_order):
                if int(watchlist_id) in ticker_watchlist_id_list:
                    # The list contains the same ticker
                    if transaction_type == TransactionType.SELL.value:
                        total_open_sell_orders += open_order.units
                    else:
                        total_open_sell_orders -= open_order.units

        if int(total_stock_units + total_bought_calls) > 0:
            # If no calls/stocks available, no covered call can be sold.
            # Check needed to not trigger spurious covered call message with open orders
            if int((total_stock_units + total_bought_calls - total_sold_calls - total_open_sell_orders)/100) > 0:
                self.__addAlertDetails(
                    scan_entry, self.__SCAN_ERROR_MSG,
                    'Missed to sell covered call? stocks={}, calls bought={}, calls sold={}, open_orders={}'
                    .format(total_stock_units, total_bought_calls, total_sold_calls, total_open_sell_orders))
            elif total_open_sell_orders > 0:
                self.__addAlertDetails(
                    scan_entry, self.__SCAN_INFO_MSG,
                    'Have open covered call orders. stocks={}, calls bought={}, calls sold={}, open_orders={}'
                    .format(total_stock_units, total_bought_calls, total_sold_calls, total_open_sell_orders))


    def __check_support_resistance_alert(self, scan_entry, watchlist, scan_data):
        # current_price contains the latest price for option or stock
        latest_price = scan_entry.current_price

        if scan_entry.resistance is None or scan_entry.resistance == 0:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'Resistance data missing.')
        elif scan_entry.resistance <= latest_price:
            change_percent = round(
                ((latest_price - scan_entry.resistance)*100/scan_entry.resistance), 2)
            self.__addAlertDetails(
                scan_entry, self.__SCAN_INFO_MSG, '{}% above resistance, . Sell?'.format(change_percent))

        if scan_entry.support is None or scan_entry.support == 0:
            self.__addAlertDetails(
                scan_entry, self.__SCAN_ERROR_MSG, 'Support data missing.')
        elif scan_entry.support >= latest_price:
            change_percent = round(
                ((latest_price - scan_entry.support)*100/scan_entry.support), 2)
            self.__addAlertDetails(
                scan_entry, self.__SCAN_INFO_MSG, '{}% below support. Buy?'.format(change_percent))

    def __check_extended_hours_price_movement_alert(self, scan_entry, watchlist, scan_data):
        if scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY] is None:
            logger.error('__check_extended_hours_price_movement_alert: latest price date missing. Skipping {}'
                .format(watchlist))
            return
        if scan_data[self.__SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY] is None:
            logger.error('__check_extended_hours_price_movement_alert: latest market hours price data missing. Skipping {}'
                .format(watchlist))
            return

        latest_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]
        market_hours_price = scan_data[self.__SCAN_DATA_MARKET_HOURS_TICKER_PRICE_DICT_KEY][watchlist.ticker]

        extended_hours_price_change = round((latest_price - market_hours_price)*100/market_hours_price, 2)

        if abs(extended_hours_price_change) >= 1:
            # Change in price more than 1% during after hours
            self.__addAlertDetails(scan_entry, self.__SCAN_WARN_MSG,
                                   '{}% change in price during extended hours. regular price={}'
                                   .format(extended_hours_price_change, market_hours_price))

    def __check_option_time_to_expiry_alert(self, scan_entry, watchlist, scan_data):
        time_to_expiry = watchlist.option_expiry - datetime.now().date()

        if time_to_expiry.days <= 5:
            self.__addAlertDetails(scan_entry, self.__SCAN_ERROR_MSG,
                                   'Expiry less than 5 days. Close?')
        elif time_to_expiry.days <= 10:
            self.__addAlertDetails(scan_entry, self.__SCAN_WARN_MSG,
                                   'Expiry less than 10 days. Close?')

    def __check_option_above_strike_alert(self, scan_entry, watchlist, scan_data):
        latest_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]

        if watchlist.option_strike <= latest_price:
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Stock price {} above strike price of {}.'
                                   .format(latest_price, watchlist.option_strike))

        elif abs(watchlist.option_strike - latest_price) <= latest_price * 5 / 100:
            # 5% of strike price
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Stock price {} within 5% strike price of {}.'
                                   .format(latest_price, watchlist.option_strike))

    def __check_option_below_strike_alert(self, scan_entry, watchlist, scan_data):
        latest_price = scan_data[self.__SCAN_DATA_LATEST_TICKER_PRICE_DICT_KEY][watchlist.ticker]

        if watchlist.option_strike >= latest_price:
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Stock price {} below strike price of {}.'
                                   .format(latest_price, watchlist.option_strike))

        elif abs(watchlist.option_strike - latest_price) >= latest_price * 5 / 100:
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
                                   'Current price is less than 10% of profit target. Buy back and sell option again?')

        if latest_option_price > scan_entry.profit_target*80/100:
            # Price reached 80% of profit target.
            self.__addAlertDetails(scan_entry, self.__SCAN_INFO_MSG,
                                   'Current price went beyond 80% of profit target. Buy back and sell option again?')

    __scan_profile_check_list = {
        ScanProfile.BUY_STOCK.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_missed_covered_call_sell_alert,
            ],
        ScanProfile.SELL_CALL.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_above_strike_alert,
                __check_option_time_to_expiry_alert,
                __check_sold_option_buyback_alert
            ],
        ScanProfile.BUY_CALL.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_below_strike_alert,
                __check_option_time_to_expiry_alert,
                __check_missed_covered_call_sell_alert
            ],
        ScanProfile.BUY_PUT.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_above_strike_alert,
                __check_option_time_to_expiry_alert,
            ],
        ScanProfile.SELL_PUT.value:
            [
                __check_support_resistance_alert,
                __check_extended_hours_price_movement_alert,
                __check_option_below_strike_alert,
                __check_option_time_to_expiry_alert,
                __check_sold_option_buyback_alert
            ],
    }

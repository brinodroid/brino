from threading import Timer
from datetime import datetime, timedelta
from django.utils import timezone

import logging
from brHistory.models import CallOptionData, PutOptionData
from brCore.models import WatchList
from brCore.types.asset_types import AssetTypes
from brCore.client.Factory import get_client

logger = logging.getLogger('django')


class Crawler:
    __instance = None
    __OPTION_TYPE_KEY = 'type'
    __OPTION_IS_PRESET_KEY = 'is_preset'
    __OPTION_SAVE_KEY = 'save'

    def __init__(self):
        """ Virtually private constructor. """
        if Crawler.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Crawler.__instance = self

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Crawler.__instance == None:
            Crawler()
        return Crawler.__instance

    def __safe_float(self, float_string):
        try:
            f = float(float_string)
            return f
        except:
            logger.info('__safe_float: Not valid number =%s', float_string)
        return 0

    def __safe_int(self, int_string):
        try:
            f = int(int_string)
            return f
        except:
            logger.info('__safe_int: Not valid number =%s', int_string)
        return 0

    def __option_history_update(self, client, option_asset_type):
        try:
            watchlist_list = WatchList.objects.filter(
                asset_type=option_asset_type)
        except WatchList.DoesNotExist:
            # Nothing to scan
            logger.info('__option_history_update: No watchlist found')
            return

        date = timezone.now().date()
        for watchlist in watchlist_list:
            logger.info(
                '__option_history_update: watchlist {}'.format(watchlist))

            if self.__crawl_option_operation[option_asset_type][self.__OPTION_IS_PRESET_KEY](self, date, watchlist.id):
                logger.info(
                    '__option_history_update: Found {} for date {} and watchlist id {}. Skipping'
                    .format(option_asset_type, date, watchlist.id))
                continue

            # Not yet added. Needs to add it.
            logger.info(
                '__option_history_update: Adding data for date {} and watchlist id {}'
                .format(date, watchlist.id))

            try:
                option_type = self.__crawl_option_operation[option_asset_type][self.__OPTION_TYPE_KEY]
                option_raw_data = client.get_option_price(watchlist.ticker,
                                                          str(watchlist.option_expiry),
                                                          str(watchlist.option_strike),
                                                          option_type)
                option_data = option_raw_data[0][0]
            except Exception as e:
                # Got exception. Continue
                logger.error(
                    '__option_history_update: get_option_price() for watchlist.id {} gave Exception: {}'
                    .format(watchlist.id, repr(e)))
                watchlist.comment = 'ERROR in fetching data'
                watchlist.save()
                continue

            self.__crawl_option_operation[option_asset_type][self.__OPTION_SAVE_KEY](
                self, watchlist.id, option_data)

        return

    def __save_call_option_history(self, watchlist_id, option_data):
        call_option_data = CallOptionData(watchlist_id=watchlist_id,
                                          mark_price=self.__safe_float(
                                              option_data['mark_price']),
                                          ask_price=self.__safe_float(
                                              option_data['ask_price']),
                                          bid_price=self.__safe_float(
                                              option_data['bid_price']),
                                          high_price=self.__safe_float(
                                              option_data['high_price']),
                                          low_price=self.__safe_float(
                                              option_data['low_price']),
                                          last_trade_price=self.__safe_float(
                                              option_data['last_trade_price']),

                                          open_interest=self.__safe_int(
                                              option_data['open_interest']),
                                          volume=self.__safe_int(
                                              option_data['volume']),
                                          ask_size=self.__safe_int(
                                              option_data['ask_size']),
                                          bid_size=self.__safe_int(
                                              option_data['bid_size']),

                                          delta=self.__safe_float(
                                              option_data['delta']),
                                          gamma=self.__safe_float(
                                              option_data['gamma']),
                                          implied_volatility=self.__safe_float(
                                              option_data['implied_volatility']),
                                          rho=self.__safe_float(
                                              option_data['rho']),
                                          theta=self.__safe_float(
                                              option_data['theta']),
                                          vega=self.__safe_float(
                                              option_data['vega'])
                                          )
        call_option_data.save()
        return

    def __save_put_option_history(self, watchlist_id, option_data):
        put_option_data = PutOptionData(watchlist_id=watchlist_id,
                                        mark_price=self.__safe_float(
                                            option_data['mark_price']),
                                        ask_price=self.__safe_float(
                                            option_data['ask_price']),
                                        bid_price=self.__safe_float(
                                            option_data['bid_price']),
                                        high_price=self.__safe_float(
                                            option_data['high_price']),
                                        low_price=self.__safe_float(
                                            option_data['low_price']),
                                        last_trade_price=self.__safe_float(
                                            option_data['last_trade_price']),

                                        open_interest=self.__safe_int(
                                            option_data['open_interest']),
                                        volume=self.__safe_int(
                                            option_data['volume']),
                                        ask_size=self.__safe_int(
                                            option_data['ask_size']),
                                        bid_size=self.__safe_int(
                                            option_data['bid_size']),

                                        delta=self.__safe_float(
                                            option_data['delta']),
                                        gamma=self.__safe_float(
                                            option_data['gamma']),
                                        implied_volatility=self.__safe_float(
                                            option_data['implied_volatility']),
                                        rho=self.__safe_float(
                                            option_data['rho']),
                                        theta=self.__safe_float(
                                            option_data['theta']),
                                        vega=self.__safe_float(
                                            option_data['vega'])
                                        )
        put_option_data.save()
        return

    def __is_put_already_in_DB(self, date, watchlist_id):
        # check if this is already in the history DB
        put_option_data = PutOptionData.objects.filter(
            date=date, watchlist_id=watchlist_id)

        if len(put_option_data) > 0:
            # We found an entry for the same date and watchlist id
            return True

        # Not present in DB
        return False

    def __is_call_already_in_DB(self, date, watchlist_id):
        # check if this is already in the history DB
        call_option_data = CallOptionData.objects.filter(
            date=date, watchlist_id=watchlist_id)

        if len(call_option_data) > 0:
            # We found an entry for the same date and watchlist id
            return True

        # Not present in DB
        return False

    __crawl_option_operation = {
        AssetTypes.PUT_OPTION.value: {
            __OPTION_TYPE_KEY: 'put',
            __OPTION_SAVE_KEY: __save_put_option_history,
            __OPTION_IS_PRESET_KEY: __is_put_already_in_DB,
        },
        AssetTypes.CALL_OPTION.value: {
            __OPTION_TYPE_KEY: 'call',
            __OPTION_SAVE_KEY: __save_call_option_history,
            __OPTION_IS_PRESET_KEY: __is_call_already_in_DB,
        }
    }

    def __save_data(self):
        # This saving is done independently of the scanner as watchlist
        # could be different from scanner

        client = get_client()

        self.__option_history_update(client, AssetTypes.CALL_OPTION.value)
        self.__option_history_update(client, AssetTypes.PUT_OPTION.value)

    def start(self):
        x = datetime.today()
        # Time specified below is in UTC.
        # 7am UTC is same as 11pm PST or 12pm PDT
        y = x.replace(day=x.day, hour=7, minute=0, second=0,
                      microsecond=0)  # + timedelta(days=1)
        if y < x:
            y = y + timedelta(days=1)
        delta_t = y-x

        secs = delta_t.seconds+1
        timer = Timer(secs, self.__save_data)
        timer.start()
        return

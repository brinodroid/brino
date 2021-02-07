import logging

from common.client.Factory import get_client
from brCore.models import WatchList, BGTask, PortFolio, ScanEntry, PortFolioUpdate
from brSetting.models import Configuration
from brCore.types.asset_types import PortFolioSource, AssetTypes, TransactionType
from brCore.types.scan_types import ScanProfile, ScanStatus

logger = logging.getLogger('django')


class PFUpdater:
    __instance = None

    __scan_profile_for_call_option_lut = {
        TransactionType.BUY.value: ScanProfile.BUY_CALL.value,
        TransactionType.SELL.value: ScanProfile.SELL_CALL.value,
    }

    __scan_profile_for_put_option_lut = {
        TransactionType.BUY.value: ScanProfile.BUY_PUT.value,
        TransactionType.SELL.value: ScanProfile.SELL_PUT.value,
    }

    def __init__(self):
        """ Virtually private constructor. """
        if PFUpdater.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            PFUpdater.__instance = self

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PFUpdater.__instance == None:
            PFUpdater()
        return PFUpdater.__instance

    def __update_option_in_watchlist(self, option_data):
        try:
            watchlist = WatchList.objects.get(asset_type=option_data['brino_asset_type'],
                                              ticker=option_data['chain_symbol'],
                                              option_strike=option_data['strike_price'],
                                              option_expiry=option_data['expiration_date'])
            # Watchlist already have the entry, just update the brine_id
            watchlist.brine_id = option_data['id']

        except WatchList.DoesNotExist:
            # Create a new watchlist
            watchlist = WatchList(asset_type=option_data['brino_asset_type'],
                                  ticker=option_data['chain_symbol'],
                                  option_strike=option_data['strike_price'],
                                  option_expiry=option_data['expiration_date'],
                                  brine_id=option_data['id'])
        watchlist.save()
        return watchlist

    def __update_option_in_portfolio(self, option, watchlist, configuration):
        # Check if its already there in portfolio
        try:
            portfolio = PortFolio.objects.get(brine_id=option['id'])
            # Portfolio already has the entry. Nothing to do
            return portfolio
        except PortFolio.DoesNotExist:
            logger.info('__update_option_in_portfolio: Adding watchlist_id to portfolio'.format(
                watchlist.id))
            # INTENTIONAL FALL DOWN. Add the entry to portfolio

        # Portfolio has to be identified by the brine_id. Add it the right brine id
        portfolio = PortFolio(watchlist_id=watchlist.id,
                              entry_datetime=option['created_at'],
                              entry_price=option['brino_entry_price']/100,
                              units=float(
                                  option['quantity'])*float(option['trade_value_multiplier']),
                              transaction_type=option['brino_transaction_type'],
                              brine_id=option['id'],
                              source=PortFolioSource.BRINE.value)
        portfolio.save()
        return portfolio

    def __get_scan_profile(self, watchlist, portfolio):
        if watchlist.asset_type == AssetTypes.STOCK.value:
            return ScanProfile.BUY_STOCK.value

        if watchlist.asset_type == AssetTypes.PUT_OPTION.value:
            return self.__scan_profile_for_put_option_lut[portfolio.transaction_type]

        # Else its call option
        return self.__scan_profile_for_call_option_lut[portfolio.transaction_type]

    def __update_scan_entry(self, watchlist, portfolio, configuration):
        profile = self.__get_scan_profile(watchlist, portfolio)

        # Check if its already there in scan
        try:
            scan_entry = ScanEntry.objects.get(
                watchlist_id=watchlist.id, profile=profile)
            # Scan has the entry, nothing to do

            #scan_entry.status = ScanStatus.NONE.value
            #scan_entry.save()
            return scan_entry
        except ScanEntry.DoesNotExist:
            logger.info('__update_option_in_scan_entry: Adding watchlist_id={}, profile={} to ScanEntry'
                        .format(watchlist.id, profile))
            # Add the entry to ScanEntry

        # ScanEntry has to be identified by the watchlist_id and profile. Adding new scan entry

        if portfolio.transaction_type == TransactionType.BUY.value:
            # When we buy,
            # 1. profit target should be more than entry_price
            # 2. stop loss should be less than entry_price
            profit_target = portfolio.entry_price * \
                (100+configuration.profitTargetPercent)/100
            stop_loss = portfolio.entry_price * \
                (100-configuration.stopLossPercent)/100

        else:
            # When we sell,
            # 1. profit target should be less than entry_price
            # 2. stop loss should be more than entry_price
            profit_target = portfolio.entry_price * \
                (100-configuration.profitTargetPercent)/100
            stop_loss = portfolio.entry_price * \
                (100+configuration.stopLossPercent)/100

        scan_entry = ScanEntry(watchlist_id=watchlist.id,
                               portfolio_id=portfolio.id,
                               profile=profile,
                               profit_target=round(profit_target, 2),
                               stop_loss=round(stop_loss, 2))
        scan_entry.save()
        return scan_entry

    def __update_deleted_scan_entries(self, brine_id_lut):
        # Search for deleted options
        portfolio_list = PortFolio.objects.filter(
            source=PortFolioSource.BRINE.value)

        for portfolio in portfolio_list:
            try:
                watchlist = WatchList.objects.get(id=portfolio.watchlist_id)
            except WatchList.DoesNotExist:
                # Log error and continue
                logger.error('__update_options: watchlist_id {} from portfolio.id MISSING'.format(
                    portfolio.watchlist_id, portfolio.id))
                continue

            if str(portfolio.brine_id) not in brine_id_lut:
                # This position is not found in the brine_id_lut.
                # Update scan object as MISSING
                try:
                    scan_entry = ScanEntry.objects.get(
                        portfolio_id=portfolio.id)
                    scan_entry.status = ScanStatus.MISSING.value
                    scan_entry.save()

                except ScanEntry.DoesNotExist:
                    # Log error and continue
                    logger.error('__update_options: scan entry MISSING with portfolio_id {}'.format(
                        portfolio.watchlist_id, portfolio.id))
        return

    def __update_options(self, client, configuration):
        option_list = client.get_my_options_list()

        brine_id_lut = {}

        # Add new options
        for option in option_list:
            # Check if we already have this in watchlist
            brine_id_lut[option['id']] = True

            try:
                watchlist = WatchList.objects.get(
                    brine_id=option['option_id'])
                #Updating the comment to recover from errors on updates to watchlist
                watchlist.comment = ''
                watchlist.save()

            except WatchList.DoesNotExist:
                # Call client to get more info
                option_data = client.get_option_data(option['option_id'])
                watchlist = self.__update_option_in_watchlist(option_data)

            # Update portfolio
            portfolio = self.__update_option_in_portfolio(
                option, watchlist, configuration)

            self.__update_scan_entry(watchlist, portfolio, configuration)

        return brine_id_lut

    def __update_stock_in_watchlist(self, stock, instrument_data):
        try:
            watchlist = WatchList.objects.get(asset_type=stock['brino_asset_type'],
                                              ticker=instrument_data['symbol'])
            # Watchlist already have the entry, just update the brine_id
            watchlist.brine_id = stock['instrument_id']
            #Updating the comment to recover from errors on updates to watchlist
            watchlist.comment = ''
        except WatchList.DoesNotExist:
            # Create a new watchlist
            watchlist = WatchList(asset_type=stock['brino_asset_type'],
                                  ticker=instrument_data['symbol'],
                                  brine_id=stock['instrument_id'])
        watchlist.save()
        return watchlist

    def __update_stock_in_portfolio(self, watchlist, stock):
        # Check if its already there in portfolio
        try:
            portfolio = PortFolio.objects.get(brine_id=stock['instrument_id'])
            # Portfolio already has the entry. Nothing to do
            return portfolio
        except PortFolio.DoesNotExist:
            logger.info('__update_stock_in_portfolio: Adding watchlist_id to portfolio'.format(
                watchlist.id))
            # INTENTIONAL FALL DOWN. Add the entry to portfolio

        # Portfolio has to be identified by the brine_id. Add it the right brine id
        portfolio = PortFolio(watchlist_id=watchlist.id,
                              entry_datetime=stock['created_at'],
                              entry_price=stock['brino_entry_price'],
                              units=float(stock['quantity']),
                              transaction_type=stock['brino_transaction_type'],
                              brine_id=stock['instrument_id'],
                              source=PortFolioSource.BRINE.value)
        portfolio.save()
        return portfolio

    def __update_stocks(self, client, configuration):
        stock_list = client.get_my_stock_list()

        brine_id_lut = {}

        for stock in stock_list:
            # Update watchlist
            brine_id_lut[stock['instrument_id']] = True
            try:
                watchlist = WatchList.objects.get(
                    brine_id=stock['instrument_id'])
                #Updating the comment to recover from errors on updates to watchlist
                watchlist.comment = ''
                watchlist.save()
            except WatchList.DoesNotExist:
                instrument_data = client.get_stock_instrument_data(
                    stock['instrument_url'])
                watchlist = self.__update_stock_in_watchlist(
                    stock, instrument_data)

            # Update portfolio
            portfolio = self.__update_stock_in_portfolio(watchlist, stock)

            # Update the scan entry
            self.__update_scan_entry(watchlist, portfolio, configuration)

        return brine_id_lut

    def update(self, source):
        # TODO:
        # 1. Need to handle other sources
        # 2. Should we do something for delete?
        # 3. Need to add for stocks too

        configuration = Configuration.objects.first()
        client = get_client(source)

        stock_ids_lut = self.__update_stocks(client, configuration)
        option_ids_lut = self.__update_options(client, configuration)

        self.__update_deleted_scan_entries({**stock_ids_lut, **option_ids_lut})

        return
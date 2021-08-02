import logging
from common.client.Factory import get_client
from common.types.asset_types import PortFolioSource, AssetTypes, TransactionType
from common.types.scan_types import ScanProfile, ScanStatus
from brCore.models import WatchList, BGTask, PortFolio, ScanEntry, PortFolioUpdate
from brOrder.models import OpenOrder, ExecutedOrder, CancelledOrder
from brSetting.models import Configuration
from django.utils import timezone


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

    __option_multiplier = 100.0

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
            logger.info('__update_option_in_portfolio: Adding watchlist_id {} to portfolio'.format(
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
            logger.info('getting scan: Adding watchlist_id={}, profile={} to ScanEntry'
                        .format(watchlist.id, profile))
            scan_entry = ScanEntry.objects.get(
                watchlist_id=watchlist.id, profile=profile)
            # Scan has the entry, nothing to do

            scan_entry.status = ScanStatus.NONE.value
            scan_entry.save()
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
                logger.error('__update_options: watchlist_id {} from portfolio.id {} MISSING'.format(
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
                        portfolio.id))
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
            logger.info('__update_stock_in_portfolio: Adding watchlist_id {} to portfolio'.format(
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

    def __update_open_option_orders_legs(self, client, open_order):
        watchlist_id_list = []
        transaction_type_list = []
        for res_leg in open_order['res_legs_list']:
            option_data = client.get_option_data(res_leg['instrument_id'])
            watchlist = self.__update_option_in_watchlist(option_data)
            watchlist_id_list.append(watchlist.id)
            transaction_type_list.append(res_leg['brino_transaction_type'])

        return watchlist_id_list, transaction_type_list

    def __convert_orders_list_to_map(self, open_orders):
        open_order_ids_list =[d['id'] for d in open_orders]
        open_orders_map = dict(zip(open_order_ids_list, open_orders))
        return open_orders_map

    def __get_order_asset_type(self, open_order_in_table):
        watchlist_id_list = open_order_in_table.watchlist_id_list.split(',')
        first_watchlist_id = watchlist_id_list[0]
        watchlist = WatchList.objects.get(
                    pk=int(first_watchlist_id))
        return watchlist.asset_type


    def __update_missing_open_orders(self, client, open_orders):
        # Get all open orders from the order table
        open_orders_in_table = OpenOrder.objects.all()
        open_orders_map = self.__convert_orders_list_to_map(open_orders)

        for open_order_in_table in open_orders_in_table:
            if str(open_order_in_table.brine_id) in open_orders_map:
                # Its still an open order, nothing to do
                logger.info('__update_missing_open_orders: Order {} is still open'.format(
                    open_order_in_table.brine_id))
                continue

            # The missing order could be either
            # Case 1: Executed. Add it to portfolio
            # Case 2: Cancelled. Add it the cancelled table and delete from here
            if self.__get_order_asset_type(open_order_in_table) == AssetTypes.STOCK.value:
                order_status = client.get_open_stock_order_status(open_order_in_table.brine_id)
            else:
                order_status = client.get_open_option_order_status(open_order_in_table.brine_id)

            logger.info('__update_missing_open_orders: order_status {} is still open'.format(
                    order_status))

            if order_status['state'] == 'cancelled':
                #Order is cancelled
                cancelled_order = CancelledOrder(watchlist_id_list=open_order_in_table.watchlist_id_list,
                    transaction_type_list=open_order_in_table.transaction_type_list,
                    created_datetime=open_order_in_table.created_datetime,
                    cancelled_datetime=order_status['updated_at'],
                    price=open_order_in_table.price,
                    units=open_order_in_table.units,
                    brine_id=open_order_in_table.brine_id,
                    closing_strategy=open_order_in_table.closing_strategy,
                    opening_strategy=open_order_in_table.opening_strategy,
                    source=open_order_in_table.source)
                cancelled_order.save()
            elif order_status['state'] == 'filled':
                #Should have been filled
                executed_order = ExecutedOrder(watchlist_id_list=open_order_in_table.watchlist_id_list,
                    transaction_type_list=open_order_in_table.transaction_type_list,
                    order_created_datetime=open_order_in_table.created_datetime,
                    executed_datetime=order_status['updated_at'],
                    price=open_order_in_table.price,
                    executed_price=order_status['brino_entry_price'],
                    units=open_order_in_table.units,
                    brine_id=open_order_in_table.brine_id,
                    closing_strategy=open_order_in_table.closing_strategy,
                    opening_strategy=open_order_in_table.opening_strategy,
                    source=open_order_in_table.source)
                executed_order.save()
            else:
                logger.error('__update_missing_open_option_orders: Order state {} is unknown. Ignoring'
                    .format(order_status))
                continue

            #delete the order from openOrders
            open_order_in_table.delete()

    def __update_open_option_orders(self, client, open_option_orders):
        for open_order in open_option_orders:
            try:
                order = OpenOrder.objects.get(
                    brine_id=open_order['id'])
                #Order is already in the Db. Nothing to do
                continue
            except OpenOrder.DoesNotExist:
                # This is a new order, need that needs to be added to Db
                logger.info('__update_open_option_orders: Adding new order {}'.format(
                    open_order))
            # INTENTIONAL FALL DOWN. Add the entry to portfolio

            watchlist_id_list, transaction_type_list = self.__update_open_option_orders_legs(client, open_order)

            watchlist_id_list_text = ','.join(map(str, watchlist_id_list))
            transaction_type_list_text = ','.join(map(str, transaction_type_list))

            # Order
            order = OpenOrder(watchlist_id_list=watchlist_id_list_text,
                            transaction_type_list=transaction_type_list_text,
                            created_datetime=open_order['created_at'],
                            price=open_order['brino_entry_price'],
                            units=float(open_order['quantity'])*self.__option_multiplier,
                            brine_id=open_order['id'],
                            closing_strategy=open_order['closing_strategy'],
                            opening_strategy=open_order['opening_strategy'],
                            source=PortFolioSource.BRINE.value)
            order.save()

        return

    def __update_open_stock_orders_legs(self, client, open_order):
        watchlist_id_list = []
        transaction_type_list = []

        instrument_data = client.get_stock_instrument_data(open_order['instrument_url'])
        watchlist = self.__update_stock_in_watchlist(open_order, instrument_data)

        watchlist_id_list.append(watchlist.id)
        transaction_type_list.append(open_order['brino_transaction_type'])

        return watchlist_id_list, transaction_type_list

    def __update_open_stock_orders(self, client, open_stock_orders):
        for open_order in open_stock_orders:
            try:
                order = OpenOrder.objects.get(
                    brine_id=open_order['id'])
                #Order is already in the Db. Nothing to do
                continue
            except OpenOrder.DoesNotExist:
                # This is a new order, need that needs to be added to Db
                logger.info('__update_open_stock_orders: Adding new order {}'.format(
                    open_order))
            # INTENTIONAL FALL DOWN. Add the entry to portfolio

            watchlist_id_list, transaction_type_list = self.__update_open_stock_orders_legs(client, open_order)

            watchlist_id_list_text = ','.join(map(str, watchlist_id_list))
            transaction_type_list_text = ','.join(map(str, transaction_type_list))

            # Order
            order = OpenOrder(watchlist_id_list=watchlist_id_list_text,
                            transaction_type_list=transaction_type_list_text,
                            created_datetime=open_order['created_at'],
                            price=open_order['brino_entry_price'],
                            units=float(open_order['quantity']),
                            brine_id=open_order['id'],
                            source=PortFolioSource.BRINE.value)
            order.save()

        return

    def __update_open_orders(self, client):
        open_option_orders = client.get_open_option_orders()
        open_stock_orders = client.get_open_stock_orders()

        self.__update_missing_open_orders(client, open_option_orders + open_stock_orders)

        #Before adding the new orders, remove
        self.__update_open_option_orders(client, open_option_orders)
        self.__update_open_stock_orders(client, open_stock_orders)


    def update(self, source):
        # TODO:
        # 1. Need to handle other sources
        # 2. Should we do something for delete?
        # 3. Need to add for stocks too

        configuration = Configuration.objects.first()
        client = get_client(source)

        self.__update_open_orders(client)

        stock_ids_lut = self.__update_stocks(client, configuration)
        option_ids_lut = self.__update_options(client, configuration)

        self.__update_deleted_scan_entries({**stock_ids_lut, **option_ids_lut})

        return
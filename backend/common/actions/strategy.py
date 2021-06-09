import time
import logging
from datetime import datetime, timedelta
import brifz
from django.db.models import Q
from common.client.Factory import get_client
from common.types.scan_types import ScanStatus, ScanProfile
from common.types.asset_types import AssetTypes, TransactionType, PortFolioSource

from brCore.models import WatchList, ScanEntry, PortFolio
from brOrder.models import OpenOrder, ExecutedOrder, CancelledOrder

logger = logging.getLogger('django')


class Strategy:
    __instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if Strategy.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Strategy.__instance = self

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Strategy.__instance == None:
            Strategy()
        return Strategy.__instance

    def run_strategy(self, scan_entry, watchlist, scan_data, client):
        if not scan_entry.active_track:
            logger.info('run_strategy: skipping strategy for {}'.format(scan_entry))
            return

        try:
            portfolio = PortFolio.objects.get(pk=scan_entry.portfolio_id)
        except PortFolio.DoesNotExist:
            logger.error('run_strategy: {} Portfolio not found'.format(
                scan_entry))
            return

        if portfolio.watchlist_id != watchlist.id:
            logger.error('run_strategy: PortFolio.watchlist_id {} mismatch with watchlist.id {}'
                .format(portfolio.watchlist_id, watchlist.id))
            return

        if portfolio.source != PortFolioSource.BRINE.value:
            #TODO: This check can be removed as we support more clients
            logger.error('run_strategy: {}, no brine_id {} in portfolio'
                .format(scan_entry, portfolio))
            return

        # Need to run strategy
        for strategy in self.__strategy_list[scan_entry.profile]:
            try:
                strategy(self, scan_entry, scan_data, watchlist, portfolio, client)
            except Exception as e:
                logger.error('run_strategy: strategy: {} gave Exception: {}'
                    .format(strategy, repr(e)))


    def __buy_stoploss(self, scan_entry, scan_data, watchlist, portfolio, client):
        #This applies to stocks and call option buys
        # current_price is below stop_loss
        if scan_entry.stop_loss > scan_entry.current_price:
            logger.info('__stock_stoploss: {} below stop_loss'.format(scan_entry))
            #1. check if we have covered calls.
            #2. We need to buy back the covered calls before selling
            #3. Sell

        return

    def __sell_call_stoploss(self, scan_entry, scan_data, watchlist, portfolio, client):
        if watchlist.asset_type != AssetTypes.CALL_OPTION.value:
            logger.error('__sell_call_stoploss: {} wrong scan profile?'.format(scan_entry))
            return

        # This means our covered call went beyond our stop loss target. Buy it back
        if scan_entry.stop_loss >= scan_entry.current_price:
            logger.info('__sell_call_stoploss: {} stop_loss not triggerred'
                .format(scan_entry))
            return

        logger.info('__sell_call_stoploss: {} above stop_loss. Buying back to close'
            .format(scan_entry))

        if not scan_entry.order_id:
            # No order placed, put in an order
            order = client.order_option_buy_close_limit('debit', scan_entry.current_price,
                watchlist.ticker, portfolio.units/100, watchlist.option_expiry.strftime('%Y-%m-%d'), watchlist.option_strike, 'call')
            if 'id' not in order:
                logger.error('__sell_call_stoploss: {} close order failed with {}'
                    .format(scan_entry, order))
                return

            # Add Order to table
            open_order_in_table = OpenOrder(watchlist_id_list=watchlist.id,
                        transaction_type_list=TransactionType.BUY.value,
                        created_datetime=order['created_at'],
                        price=scan_entry.current_price,
                        units=portfolio.units,
                        brine_id=order['id'],
                        closing_strategy=order['closing_strategy'],
                        opening_strategy=order['opening_strategy'],
                        source=PortFolioSource.BRINE.value)
            open_order_in_table.save()

            # Order closing triggered.
            scan_entry.order_id = open_order_in_table.id

        # There is a pending order, track status of the order
        try:
            open_order_in_table = OpenOrder.objects.get(pk=scan_entry.order_id)
        except OpenOrder.DoesNotExist:
            logger.error('run_strategy: {} OpenOrder not found'.format(
            scan_entry))
            return

        order_status = client.get_open_option_order_status(open_order_in_table.brine_id)
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
            logger.info('__sell_call_stoploss: Order state {} is not cancelled or filled. Ignoring'
                .format(order_status))
            return

        # This means the order got executed or cancelled.
        #delete the order from openOrders. Stop tracking it
        open_order_in_table.delete()
        scan_entry.active_track = False
        scan_entry.order_id = None

        return

    def __stoploss(self, scan_entry, scan_data, watchlist, portfolio, client):
        # current_price contains the latest price for option or stock
        return

    
    __strategy_list = {
        ScanProfile.BUY_STOCK.value:
            [
                __buy_stoploss
            ],
        ScanProfile.SELL_CALL.value:
            [
                __sell_call_stoploss
            ],
        ScanProfile.BUY_CALL.value:
            [
                __buy_stoploss
            ],
        ScanProfile.BUY_PUT.value:
            [
                __stoploss
            ],
        ScanProfile.SELL_PUT.value:
            [
                __stoploss
            ],
    }

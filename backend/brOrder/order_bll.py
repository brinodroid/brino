import logging
from datetime import datetime, timedelta
import brCore.watchlist_bll as watchlist_bll
import brCore.scanentry_bll as scanentry_bll
import brCore.portfolio_bll as portfolio_bll
import brHistory.history_bll as history_bll
from brOrder.models import OpenOrder, ExecutedOrder, CancelledOrder
from brOrder.order_types import OrderAction
from common.types.asset_types import AssetTypes, TransactionType, PortFolioSource
from common.client.Factory import get_client
import common.utils as utils

logger = logging.getLogger('django')

def poll_order_status():
    # get all openOrders
    try:
        open_orders_list = OpenOrder.objects.all()
    except OpenOrder.DoesNotExist:
        # Nothing to scan
        logger.info('poll_order_status: No open orders')
        return

    # check its status in brine
    for open_order in open_orders_list:
        logger.info('poll_order_status: checking {}'.format(open_order))
        if not _open_order_check(open_order):
            # Order is either cancelled or executed.
            open_order.delete()

    return

def delete_order(order):
    # Delete really means mvoing the order to CancelledOrder or ExecutedOrder

    order_cancelled = True
    order_terminated_time = datetime.now()

    # This order has been submitted
    order_status = _get_order_status(order)
    if order_status and order_status['state'] != 'cancelled':
        # Order status is valid. Check to see if it needs to be cancelled
        if order_status['state'] == 'filled' :
            order_cancelled = False
            order_terminated_time = order_status['updated_at']
        else :
            # Cancel the order
            _cancel_order(order)

    if order_cancelled:
        # Move to CancelledOrder if the order is cancelled.
        cancelled_order = CancelledOrder(watchlist_id_list=order.watchlist_id_list,
                transaction_type_list=order.transaction_type_list,
                created_datetime=order.created_datetime,
                cancelled_datetime=order_terminated_time,
                price=order.price,
                units=order.units,
                brine_id=order.brine_id,
                closing_strategy=order.closing_strategy,
                opening_strategy=order.opening_strategy,
                source=order.source)
        cancelled_order.save()
    else:
        # Move to ExecutedOrder if the order is executed
        executed_order = ExecutedOrder(watchlist_id_list=order.watchlist_id_list,
                transaction_type_list=order.transaction_type_list,
                created_datetime=order.created_datetime,
                cancelled_datetime=order_terminated_time,
                price=order.price,
                units=order.units,
                brine_id=order.brine_id,
                closing_strategy=order.closing_strategy,
                opening_strategy=order.opening_strategy,
                source=order.source)
        executed_order.save()

        portfolio = portfolio_bll.create_if_not_exists(executed_order)

        # Update strategy to point to portfolio
        strategy_bll.update_portfolio(order.strategy_id, portfolio)

    order.delete()

    return order


def submit_limit_order(serializer, strategy, watchlist):
    if watchlist_bll.is_option(watchlist):
        # Add option price history
        history_bll.create_option_history(watchlist)

    # Create a scan entry if not already existing
    scan_entry = scanentry_bll.create_if_not_exists(watchlist, serializer.validated_data['price'],
        serializer.validated_data['transaction_type_list'])

    strategy = strategy_bll.create_strategy(strategy, scan_entry)

    if serializer.validated_data['submit']:
        if 'action' in serializer.validated_data.keys():
            action = serializer.validated_data['action']
        else:
            # Defaulting to open
            action = OrderAction.OPEN.value

        #Submit the call to client.
        open_order = _submit_limit_order_to_client(watchlist,
            serializer.validated_data['transaction_type_list'],
            serializer.validated_data['units'],
            serializer.validated_data['price'],
            action)
    else:
        open_order = serializer.save()

    if strategy:
        # Update the strategy_id
        open_order.strategy_id = strategy.id
        open_order.save()

    return open_order



#########################################################################
## Private functions
#########################################################################

def _open_order_check(open_order):
    order_pending = True
    if not open_order.brine_id:
        logger.error('_check_and_update_order: brine_id missing. Cannot check order status: {}'
                        .format(open_order))
        return order_pending

    # We have a valid brine_id

    # This order has been submitted
    order_status = _get_order_status(open_order)
    if order_status:
        if order_status['state'] == 'cancelled':
            logger.info('_check_and_update_order: cancelled order: {}'
                        .format(open_order))

            # Order cancelled
            cancelled_order = CancelledOrder(watchlist_id_list=open_order.watchlist_id_list,
                transaction_type_list=open_order.transaction_type_list,
                created_datetime=open_order.created_datetime,
                cancelled_datetime=order_status['updated_at'],
                price=open_order.price,
                units=open_order.units,
                brine_id=open_order.brine_id,
                closing_strategy=open_order.closing_strategy,
                opening_strategy=open_order.opening_strategy,
                source=open_order.source)
            cancelled_order.save()

            # Order is not pending
            order_pending = False

        elif order_status['state'] == 'filled':
            logger.info('_check_and_update_order: filled order: {}'
                        .format(open_order))

            # Order executed
            executed_order = ExecutedOrder(watchlist_id_list=open_order.watchlist_id_list,
                transaction_type_list=open_order.transaction_type_list,
                order_created_datetime=open_order.created_datetime,
                executed_datetime=order_status['updated_at'],
                price=open_order.price,
                executed_price=order_status['brino_entry_price'],
                units=open_order.units,
                brine_id=open_order.brine_id,
                closing_strategy=open_order.closing_strategy,
                opening_strategy=open_order.opening_strategy,
                source=open_order.source)
            executed_order.save()

            # Create portolio entry
            portfolio = portfolio_bll.create_if_not_exists(executed_order)

            # Update strategy to point to portfolio
            strategy_bll.update_portfolio(open_order.strategy_id, portfolio)

            # Order is not pending
            order_pending = False
        else:
            logger.info('_check_and_update_order: Order state is {}. Ignoring'
                .format(order_status))

    return order_pending




def _cancel_order(order):
    if not order.brine_id:
        logger.error('_cancel_order: No brine_id in order. Not submitted?: {}'
                        .format(order))
        return None
    # We have a valid brine_id

    watchlist_list = order.watchlist_id_list

    # TODO: Needs to handle multiple watchlist in the order
    watchlist = watchlist_bll.get_watchlist(int(watchlist_list))

    client = get_client()

    if watchlist_bll.is_option(watchlist):
        # This is an option order
        option_order = client.cancel_option_order(order.brine_id)
        return option_order

    # This is a stock order
    stock_order = client.cancel_stock_order(order.brine_id)

    return stock_order

def _get_order_status(order):
    if not order.brine_id:
        logger.error('_get_order_status: No brine_id in order. Not submitted?: {}'
                        .format(order))
        return None

    # We have a valid brine_id

    watchlist_list = order.watchlist_id_list

    # TODO: Needs to handle multiple watchlist in the order
    watchlist = watchlist_bll.get_watchlist(int(watchlist_list))

    client = get_client()

    if watchlist_bll.is_option(watchlist):
        # This is an option order
        option_order = client.get_open_option_order_status(order.brine_id)
        return option_order

    # This is a stock order
    stock_order = client.get_open_stock_order_status(order.brine_id)

    return stock_order

def _convert_string_to_list(string_as_list):
    # Remove the square brackets[] in the string
    trimmed_string = string_as_list[1:-1]
    li = list(string_as_list.split(','))
    return li

def _update_open_stock_orders_legs(watchlist, submitted_order, client):
    watchlist_id_list = []
    transaction_type_list = []

    instrument_data = client.get_stock_instrument_data(submitted_order['instrument_url'])

    watchlist_id_list.append(watchlist.id)
    transaction_type_list.append(submitted_order['brino_transaction_type'])

    return watchlist_id_list, transaction_type_list

def _save_submitted_stock_order(watchlist, submitted_order, client):
    watchlist_id_list, transaction_type_list = _update_open_stock_orders_legs(watchlist, submitted_order, client)

    #TODO: Handle watchlist and transaction being a list
    open_order = OpenOrder(watchlist_id_list=watchlist.id,
                    transaction_type_list=submitted_order['brino_transaction_type'],
                    created_datetime=submitted_order['created_at'],
                    price=submitted_order['brino_entry_price'],
                    units=float(submitted_order['quantity']),
                    brine_id=submitted_order['id'],
                    source=PortFolioSource.BRINE.value)
    open_order.save()
    return open_order


def _submit_limit_order_to_client(watchlist, transaction_type, units, price, action):
    client = get_client()

    if watchlist_bll.is_option(watchlist):
        return _submit_option_limit_order_to_client(watchlist, transaction_type, units, price, action, client)

    # Its a stock
    submitted_order = _submit_stock_limit_order_to_client(watchlist, transaction_type, units, price, client)

    return _save_submitted_stock_order(watchlist, submitted_order, client)

def _submit_stock_limit_order_to_client(watchlist, transaction_type, units, price, client):
    if transaction_type == TransactionType.BUY.value:
        #Its a buy order
        return client.order_stock_buy_limit(watchlist.ticker, units, price)

    #Its a sell order
    return client.order_stock_sell_limit(watchlist.ticker, units, price)

def _update_open_option_orders_legs(watchlist, open_order, client):
    watchlist_id_list = []
    transaction_type_list = []
    for res_leg in open_order['res_legs_list']:
        option_data = client.get_option_data(res_leg['instrument_id'])
        watchlist_id_list.append(watchlist.id)
        transaction_type_list.append(res_leg['brino_transaction_type'])

    return watchlist_id_list, transaction_type_list

def _save_submitted_option_order(watchlist, submitted_order, client):
    watchlist_id_list, transaction_type_list = _update_open_option_orders_legs(watchlist, submitted_order, client)

    # TODO: Handle list of watchlist and transaction type
    watchlist_id_list_text = watchlist_id_list[0]
    transaction_type_list_text = transaction_type_list[0]

    # Order
    open_order = OpenOrder(watchlist_id_list=watchlist_id_list_text,
                    transaction_type_list=transaction_type_list_text,
                    created_datetime=submitted_order['created_at'],
                    price=submitted_order['brino_entry_price'],
                    units=float(submitted_order['quantity'])*utils.option_unit_multiplier,
                    brine_id=submitted_order['id'],
                    closing_strategy=submitted_order['closing_strategy'],
                    opening_strategy=submitted_order['opening_strategy'],
                    source=PortFolioSource.BRINE.value)
    open_order.save()

    return open_order

def _submit_option_limit_order_to_client(watchlist, transaction_type, units, price, action, client):
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        option_type = 'call'
    else:
        option_type = 'put'

    if action == OrderAction.OPEN.value:
        action_effect = 'open'
    else:
        action_effect = 'close'

    option_unit = units/utils.option_unit_multiplier

    if transaction_type == TransactionType.BUY.value:
        #Its a buy order
        submitted_order = client.order_option_buy_limit(action_effect, 'debit', price, watchlist.ticker,
            option_unit, watchlist.option_expiry.strftime('%Y-%m-%d'), watchlist.option_strike, option_type)
    else:
        #Its a sell order
        submitted_order = client.order_option_sell_limit(action_effect, 'credit', price, watchlist.ticker,
            option_unit, watchlist.option_expiry.strftime('%Y-%m-%d'), watchlist.option_strike, option_type)
    
    return _save_submitted_option_order(watchlist, submitted_order, client)

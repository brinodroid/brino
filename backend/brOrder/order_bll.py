import logging
from datetime import datetime, timedelta
import brCore.watchlist_bll as watchlist_bll
import brCore.scanentry_bll as scanentry_bll
import brHistory.history_bll as history_bll
import brStrategy.strategy_bll as strategy_bll
from brOrder.models import OpenOrder
from brOrder.order_types import OrderAction
from common.types.asset_types import AssetTypes, TransactionType, PortFolioSource
from common.client.Factory import get_client

logger = logging.getLogger('django')


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


def _update_open_stock_orders_legs(watchlist, submitted_order, client):
    watchlist_id_list = []
    transaction_type_list = []

    instrument_data = client.get_stock_instrument_data(submitted_order['instrument_url'])

    watchlist_id_list.append(watchlist.id)
    transaction_type_list.append(submitted_order['brino_transaction_type'])

    return watchlist_id_list, transaction_type_list

def _save_submitted_stock_order(watchlist, submitted_order, client):
    watchlist_id_list, transaction_type_list = _update_open_stock_orders_legs(watchlist, submitted_order, client)

    open_order = OpenOrder(watchlist_id_list=watchlist_id_list,
                    transaction_type_list=transaction_type_list,
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
        watchlist = watchlist_bll.get_watchlist(option_data['brino_asset_type'],
                        option_data['chain_symbol'],
                        option_data['strike_price'],
                        option_data['expiration_date'])
        watchlist_id_list.append(watchlist.id)
        transaction_type_list.append(res_leg['brino_transaction_type'])

    return watchlist_id_list, transaction_type_list

def _save_submitted_option_order(watchlist, submitted_order, client):
    watchlist_id_list, transaction_type_list = _update_open_option_orders_legs(watchlist, submitted_order, client)

    watchlist_id_list_text = ','.join(map(str, watchlist_id_list))
    transaction_type_list_text = ','.join(map(str, transaction_type_list))

    # Order
    open_order = OpenOrder(watchlist_id_list=watchlist_id_list_text,
                    transaction_type_list=transaction_type_list_text,
                    created_datetime=submitted_order['created_at'],
                    price=submitted_order['brino_entry_price'],
                    units=float(submitted_order['quantity'])*100,
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

    option_unit = units/100

    if transaction_type == TransactionType.BUY.value:
        #Its a buy order
        submitted_order = client.order_option_buy_open_limit(action_effect, 'debit', price, watchlist.ticker,
            option_unit, watchlist.option_expiry.strftime('%Y-%m-%d'), watchlist.option_strike, option_type)
    else:
        #Its a sell order
        submitted_order = client.order_sell_option_limit(action_effect, 'credit', price, watchlist.ticker,
            option_unit, watchlist.option_expiry.strftime('%Y-%m-%d'), watchlist.option_strike, option_type)
    
    return _save_submitted_option_order(watchlist, submitted_order, client)

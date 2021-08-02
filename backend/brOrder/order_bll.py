import logging
from datetime import datetime, timedelta
import brCore.watchlist_bll as watchlist_bll
import brCore.scanentry_bll as scanentry_bll
import brHistory.history_bll as history_bll
import brStrategy.strategy_bll as strategy_bll
from brOrder.models import OpenOrder
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
        #Submit the call to client.
        open_order = _submit_limit_order_to_client(watchlist,
            serializer.validated_data['transaction_type_list'],
            serializer.validated_data['units'],
            serializer.validated_data['price'])
    else:
        open_order = serializer.save()

    if strategy:
        # Connect order with strategy
        open_order.strategy_id = strategy.id
        open_order.save()

    # Successfully submited the order. Save it in DB
    return serializer.save()


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


def _submit_limit_order_to_client(watchlist, transaction_type, units, price):
    client = get_client()

    if watchlist_bll.is_option(watchlist):
        return _submit_option_limit_order_to_client(watchlist, units, price, client)

    # Its a stock
    submitted_order = _submit_stock_limit_order_to_client(watchlist, transaction_type, units, price, client)

    return _save_submitted_stock_order(watchlist, submitted_order, client)

def _submit_stock_limit_order_to_client(watchlist, transaction_type, units, price, client):
    if transaction_type == TransactionType.BUY.value:
        #Its a buy order
        return client.order_stock_buy_limit(watchlist.ticker, units, price)

    #Its a sell order
    return client.order_stock_sell_limit(watchlist.ticker, units, price)

def _submit_option_limit_order_to_client(watchlist, transaction_type, units, price, client):
    if watchlist.asset_type == AssetTypes.CALL_OPTION.value:
        option_type = 'call'
    else:
        option_type = 'put'

    if transaction_type == TransactionType.BUY.value:
        #Its a buy order
        # TODO: Have a field for effect: open/close
        return client.order_option_buy_open_limit('open', creditOrDebit, price, watchlist.ticker,
            units, watchlist.option_expiry, watchlist.option_strike, option_type)
    
    #Its a sell order
    return client.order_stock_sell_limit(watchlist.ticker, units, price)

def _submit_put_option_limit_order_to_client(watchlist, transaction_type, units, price, client):
    return
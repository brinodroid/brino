import logging
from datetime import datetime, timedelta
import brCore.watchlist_bll as watchlist_bll
import brCore.scanentry_bll as scanentry_bll
import brHistory.history_bll as history_bll
import brStrategy.strategy_bll as strategy_bll
from brCore.models import ScanEntry
from common.types.asset_types import AssetTypes, TransactionType
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
        #Submit the call to client
        _submit_limit_order_to_client(serializer.validated_data, watchlist)

    # Successfully submited the order. Save it in DB
    serializer.save()

    return 

def _submit_limit_order_to_client(order_validated_data, watchlist):
    client = get_client()

    if watchlist_bll.is_option(watchlist):
        return _submit_option_limit_order_to_client(order_validated_data, watchlist, client)

    # Its a stock
    return _submit_stock_limit_order_to_client(order_validated_data, watchlist, client)


def _submit_option_limit_order_to_client(order_validated_data, watchlist, client):

    return

def _submit_stock_limit_order_to_client(order_validated_data, watchlist, client):
    if order_validated_data['transaction_type_list'] == TransactionType.BUY.value:
        #Its a buy order
        return client.order_stock_buy_limit(watchlist.ticker, 
                        order_validated_data['units'],
                        order_validated_data['price'])
    
    #Its a sell order
    return client.order_stock_sell_limit(watchlist.ticker,
                    order_validated_data['units'],
                    order_validated_data['price'])


import logging
from datetime import datetime, timedelta
import brCore.watchlist_bll as watchlist_bll
import brCore.scanentry_bll as scanentry_bll
import brHistory.history_bll as history_bll
from brCore.models import ScanEntry
from common.client.Factory import get_client

logger = logging.getLogger('django')


def submit_order(order_validated_data, strategy, watchlist):
    if watchlist_bll.is_option(watchlist):
        # Add option price history
        history_bll.create_option_history(watchlist)

    # Create a scan entry if not already existing
    scanentry_bll.create_if_not_exists(watchlist, order_validated_data['price'],
        order_validated_data['transaction_type_list'])

    if order_validated_data['submit']:
        #Submit the call to client
        _submit_order_to_client(order_validated_data, strategy, watchlist)

    return

def _submit_order_to_client(order_validated_data, strategy, watchlist):
    client = get_client()
    #TODO: Fill in

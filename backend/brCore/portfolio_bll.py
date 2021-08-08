import logging
from datetime import datetime, timedelta

from brCore.models import WatchList, PortFolio
from brOrder.models import ExecutedOrder

logger = logging.getLogger('django')

def create_if_not_exists(executed_order):
    # Check if its already there in portfolio
    try:
        portfolio = PortFolio.objects.get(brine_id=executed_order.brine_id)
              
        # Portfolio already has the entry. Nothing to do
        return portfolio
    except PortFolio.DoesNotExist:
        logger.info('create_if_not_exists: Adding watchlist_id {} to portfolio'.format(
            executed_order.watchlist_id_list))
        # INTENTIONAL FALL DOWN. Add the entry to portfolio

    # Portfolio has to be identified by the brine_id. Add it the right brine id
    portfolio = PortFolio(watchlist_id=executed_order.watchlist_id_list,
                            entry_datetime=executed_order.update_timestamp,
                            entry_price=executed_order.price,
                            units=executed_order.units,
                            transaction_type=executed_order.transaction_type_list,
                            brine_id=executed_order.brine_id,
                            source=executed_order.source)
    portfolio.save()
    return portfolio
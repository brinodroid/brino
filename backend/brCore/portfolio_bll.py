import logging
from datetime import datetime, timedelta

from brCore.models import WatchList, PortFolio
from brOrder.models import ExecutedOrder

logger = logging.getLogger('django')

def get_all_portfolios_for_ticker(watchlists):
    res_portfolio_list = []
    for watchlist in watchlists:
        portfolio_list = PortFolio.objects.filter(watchlist_id=watchlist.id)
        res_portfolio_list += portfolio_list

    return res_portfolio_list

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

def get_portfolio(portfolio_id):
    try:
        portfolio = PortFolio.objects.get(pk=portfolio_id)
        return portfolio
    except PortFolio.DoesNotExist:
        logger.error('get_portfolio: portfolio_id {} missing'.format(portfolio_id))

    return None

def filter_by_source(source):
    portfolio_list = PortFolio.objects.filter(source=source)
    return portfolio_list

def filter_by_brine_id(brine_id):
    portfolio_list = PortFolio.objects.filter(brine_id=brine_id)
    return portfolio_list

def delete_invalid(portfolio_list):
    new_portfolio_list = []
    for portfolio in portfolio_list:
        if portfolio.units > 0:
            # Portfolio has units. This is a valid portfolio
            new_portfolio_list.append(portfolio)
        else:
            logger.info('delete_invalid: delete {}'.format(portfolio))

            # delete the portfolio. Its invalid
            portfolio.delete()

    return new_portfolio_list


def compute_total_units(portfolio_list):
    total_units = 0
    for portfolio in portfolio_list:
        total_units += portfolio.units

    return total_units

def sell_portfolio_fifo(portfolio_list, units_sold):
    # Assumption, FIFO. Older portfolios are expected to be in the list first
    for portfolio in portfolio_list:
        if portfolio.units > units_sold:
            logger.info('sell_portfolio_fifo: Sold {} units in portfolio. Updating'.format(
                portfolio, units_sold))
            portfolio.units -= units_sold
            portfolio.save()
            return 0
        else:
            units_sold -= portfolio.units

            logger.info('sell_portfolio_fifo: Sold {} completely. Deleting. Updated units {}'.format(
                portfolio, units_sold))

            portfolio.delete()
            if units_sold <= 0:
                return 0

    # Non zero units_sold indicates that portfolio is not updated
    return units_sold

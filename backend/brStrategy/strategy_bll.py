import logging
from brStrategy.models import Strategy
import brCore.watchlist_bll as watchlist_bll
from brStrategy.strategy_types import StrategyType
from brStrategy.serializer import StrategySerializer
import brCore.portfolio_bll as portfolio_bll
import brCore.watchlist_bll as watchlist_bll
import brOrder.order_bll as order_bll
import brSetting.settings_bll as settings_bll
from brOrder.order_types import OrderAction
from common.client.Factory import get_client
from common.types.asset_types import AssetTypes, TransactionType
import common.utils as utils


logger = logging.getLogger('django')


def create_strategy(strategy_user_request, scan_entry):

    serializer = StrategySerializer(data=strategy_user_request)
    if serializer.is_valid() == False:
        logger.error(serializer.errors)
        raise ValueError('Strategy serializing error:' + serializer.errors)

    strategy_type = serializer.validated_data['strategy_type']
    if 'profit_target' in serializer.validated_data.keys():
        profit_target = serializer.validated_data['profit_target']
    else:
        profit_target = scan_entry.profit_target

    if 'stop_loss' in serializer.validated_data.keys():
        stop_loss = serializer.validated_data['stop_loss']
    else:
        stop_loss = scan_entry.stop_loss

    strategy = Strategy(strategy_type=strategy_type,
                        profit_target=profit_target,
                        stop_loss=stop_loss,
                        active_track=serializer.validated_data['active_track'])

    strategy.save()

    return strategy


def create_strategy(strategy_user_request):
    serializer = StrategySerializer(data=strategy_user_request)
    if serializer.is_valid() == False:
        logger.error(serializer.errors)
        raise ValueError('Strategy serializing error:' + serializer.errors)

    strategy_type = serializer.validated_data['strategy_type']

    profit_target = 0
    if 'profit_target' in serializer.validated_data.keys():
        # Take the user provided profit_target
        profit_target = serializer.validated_data['profit_target']

    stop_loss = 0
    if 'stop_loss' in serializer.validated_data.keys():
        # Take the user provided stop_loss
        stop_loss = serializer.validated_data['stop_loss']

    # Check if we have a valid portfolio
    if 'portfolio_id' in serializer.validated_data.keys():
        portfolio_id = serializer.validated_data['portfolio_id']

        # Get the portfolio from Id
        portfolio = portfolio_bll.get_portfolio(portfolio_id)
        if portfolio == None:
            logger.error(
                "create_strategy: Cannot find portfolio_id {}".format(portfolio_id))
            raise ValueError(
                'Strategy given invalid portfolio_id ' + str(portfolio_id))

        """if not _validate_strategy(strategy_type, portfolio):
            logger.error("create_strategy: strategy_type {} cannot be applied on portfolio {}"
                         .format(strategy_type, portfolio))
            raise ValueError(
                'Strategy type doesnt apply to portfolio ' + str(portfolio_id)) """

        if 'profit_target' not in serializer.validated_data.keys():
            # User have not provided profit_target. Compute profit target
            profit_target = settings_bll.compute_profit_target(portfolio.entry_price,
                                                               portfolio.transaction_type)

        if 'stop_loss' not in serializer.validated_data.keys():
            # User have not provided stop_loss. Compute it
            stop_loss = settings_bll.compute_stop_loss(portfolio.entry_price,
                                                       portfolio.transaction_type)

    if 'portfolio_id' in serializer.validated_data.keys():
        # Include portfolio_id to save
        strategy = Strategy(strategy_type=strategy_type,
                            profit_target=profit_target,
                            stop_loss=stop_loss,
                            watchlist_id=portfolio.watchlist_id,
                            portfolio_id=portfolio_id,
                            active_track=serializer.validated_data['active_track'])
    else:
        # Do not include portfolio_id
        strategy = Strategy(strategy_type=strategy_type,
                            profit_target=profit_target,
                            stop_loss=stop_loss,
                            active_track=serializer.validated_data['active_track'])

    strategy.save()

    return strategy


def update_portfolio(strategy_id, portfolio):
    # Update the strategy to have portfolio Id after execution of the order
    try:
        strategy = Strategy.objects.get(pk=strategy_id)

        strategy.portfolio_id = portfolio.id
        # Make the strategy active now
        strategy_id.active_track = True

        strategy.save()
        return strategy
    except Strategy.DoesNotExist:
        logger.error('update_portfolio: strategy_id {} missing. portfolio_id {}'
                     .format(strategy_id, portfolio.id))

    return None


def strategy_run():
    active_strategy_list = Strategy.objects.filter(active_track=True)
    if len(active_strategy_list) == 0:
        # Nothing to scan
        logger.info('strategy_run: No active strategies')
        return

    # Update the latest order status
    order_bll.poll_order_status()

    # Strategy should go through the below states
    # 1. Active_track
    # 2. When conditions met, place closing order
    # 3. Track order status
    # 4. Deactivate after order is executed

    for active_strategy in active_strategy_list:
        portfolio = portfolio_bll.get_portfolio(active_strategy.portfolio_id)
        if portfolio is None:
            logger.info(
                'strategy_run: Missing portfolio for {}'.format(active_strategy))
            continue

        watchlist = watchlist_bll.get_watchlist(portfolio.watchlist_id)
        latest_price = watchlist_bll.get_watchlist_latest_price(watchlist, True)
        if latest_price == 0:
            logger.info('strategy_run: skipping strategy {} for watchlist {} as price is zero'.format(
                active_strategy, watchlist))
            continue

        deactivate = False
        # TODO: use strategy type. Assume covered call
        if portfolio.transaction_type == TransactionType.BUY.value:
            deactivate = _buy_strategy(
                active_strategy, portfolio, watchlist, latest_price)
        elif portfolio.transaction_type == TransactionType.SELL.value:
            deactivate = _sell_strategy(
                active_strategy, portfolio, watchlist, latest_price)
        else:
            logger.error('strategy_run: Invalid trasaction type? {}'.format(
                portfolio.transaction_type))

        _update_strategy(active_strategy, watchlist.id, deactivate, latest_price)

    return


def _update_strategy(strategy, watchlist_id, deactivate, latest_price):
    if strategy.active_track:
        strategy.active_track = not deactivate

    strategy.watchlist_id = watchlist_id
    strategy.last_price = latest_price

    # Update the highest price
    if strategy.highest_price is None:
        strategy.highest_price = latest_price
    elif strategy.highest_price < latest_price:
        strategy.highest_price = latest_price

    # Update the lowest_price price
    if strategy.lowest_price is None:
        strategy.lowest_price = latest_price
    elif strategy.lowest_price > latest_price:
        strategy.lowest_price = latest_price

    logger.info('_update_strategy: strategy {}'.format(strategy))
    strategy.save()
    return


def _sell_strategy(strategy, portfolio, watchlist, latest_price):
    logger.info('_sell_strategy: strategy {}, portfolio {}, latest_price {}'.format(
        strategy, portfolio, latest_price))

    # For sell strategy, we should buy back if
    # 1. current price is higher than stop_loss
    # 2. current price is lower than profit_target
    if latest_price > strategy.stop_loss or latest_price < strategy.profit_target:
        # Buy back to close at market
        logger.info('_sell_strategy: buying back to close strategy {}, portfolio {}, latest_price {}'.format(
            strategy, portfolio, latest_price))

        order_bll.submit_market_order_to_client(
            watchlist, TransactionType.BUY.value, portfolio.units, OrderAction.CLOSE.value)
        return True

    return False


def _buy_strategy(strategy, portfolio, watchlist, latest_price):
    logger.info('_buy_strategy: strategy {}, portfolio {}, latest_price {}'.format(
        strategy, portfolio, latest_price))
    # For buy strategy, we should buy back if
    # 1. current price is lower than stop_loss
    # 2. current price is higher than profit_target
    if latest_price < strategy.stop_loss:
        # Sell to close at market
        logger.info('_buy_strategy: selling as below stoploss strategy {}, portfolio {}, latest_price {}'.format(
            strategy, portfolio, latest_price))

        _submit_sell_order(watchlist, portfolio)
        return True

    if latest_price > strategy.profit_target:

        if latest_price > strategy.last_price:
            # The price is increasing. Hold on to capture the max profit
            logger.info('_buy_strategy: not selling yet as price is on upswing strategy {}, portfolio {}, latest_price {}'.format(
                strategy, portfolio, latest_price))

            return False

        logger.info('_buy_strategy: selling as above profit target strategy {}, portfolio {}, latest_price {}'.format(
            strategy, portfolio, latest_price))

        _submit_sell_order(watchlist, portfolio)
        return True

    return False

def _submit_sell_order(watchlist, portfolio):
    watchlists_for_ticker = watchlist_bll.get_all_watchlists_for_ticker(
        watchlist.ticker)

    # 1. Check all portfolios
    portfolios_list = portfolio_bll.get_all_portfolios_for_ticker(
        watchlists_for_ticker)

    # 2. Check if we have any open sell orders on the ticker
    open_orders_list = order_bll.get_open_orders(watchlists_for_ticker)

    # 3. _prepare_for_sell_order
    if _prepare_for_sell_order(portfolio, watchlists_for_ticker, portfolios_list, open_orders_list):
        order_bll.submit_market_order_to_client(
            watchlist, TransactionType.SELL.value, portfolio.units, OrderAction.CLOSE.value)

    return True

def _prepare_for_sell_order(portfolio_to_sell, watchlists_for_ticker, portfolio_list, open_orders_list):
    logger.info('_prepare_for_sell_order: portfolio_to_sell {}, portfolio_list {}, open_orders_list {}'.format(
        portfolio_to_sell, portfolio_list, open_orders_list))

    # Make a watchlist LUT for faster lookup
    watchlists_dict = {
        watchlist.id: watchlist for watchlist in watchlists_for_ticker}

    total_stocks = 0
    total_bought_calls = 0
    total_sold_calls = 0
    total_open_sell_orders = 0

    for portfolio in portfolio_list:
        watchlist = watchlists_dict[portfolio.watchlist_id]
        if watchlist.asset_type == AssetTypes.STOCK.value:
            total_stocks += portfolio.units
        elif watchlist.asset_type == AssetTypes.CALL_OPTION.value:
            if portfolio.transaction_type == TransactionType.BUY.value:
                total_bought_calls = portfolio.units
            else:
                total_sold_calls = portfolio.units

    for open_order in open_orders_list:
        watchlist_id_list_in_order = open_order.watchlist_id_list.split(',')
        transaction_type_list_in_order = open_order.transaction_type_list.split(
            ',')

        for (watchlist_id, transaction_type) in zip(watchlist_id_list_in_order, transaction_type_list_in_order):
            watchlist = watchlists_dict[utils.safe_int(watchlist_id)]
            # The list contains the same ticker
            if transaction_type == TransactionType.SELL.value:
                total_open_sell_orders += open_order.units
            else:
                total_open_sell_orders -= open_order.units

    logger.info('_prepare_for_sell_order: portfolio_to_sell {}, total_stocks {}, total_bought_calls {}, total_sold_calls {}, total_open_sell_orders {}'
                .format(portfolio_to_sell, total_stocks, total_bought_calls, total_sold_calls, total_open_sell_orders))

    if (total_stocks + total_bought_calls - total_sold_calls - total_open_sell_orders) >= portfolio_to_sell.units:
        # Nothing needs to be done to sell the portfolio
        logger.info('_prepare_for_sell_order: ready to sell portfolio_to_sell {}'.format(
            portfolio_to_sell))
        return True

    cancelled_orders = 0
    # Check if we can make space by cancelling some open orders
    for open_order in open_orders_list:
        watchlist_id_list_in_order = open_order.watchlist_id_list.split(',')
        transaction_type_list_in_order = open_order.transaction_type_list.split(',')

        for (watchlist_id, transaction_type) in zip(watchlist_id_list_in_order, transaction_type_list_in_order):
            watchlist = watchlists_dict[utils.safe_int(watchlist_id)]
            # The list contains the same ticker
            if transaction_type == TransactionType.SELL.value:
                # Delete the order
                order_bll.delete_order(open_order)
                logger.info('_prepare_for_sell_order: portfolio_to_sell {}, deleted order {}'.format(
                    portfolio_to_sell, open_order))

                total_open_sell_orders -= open_order.units
                cancelled_orders += open_order.units
                if cancelled_orders >= portfolio_to_sell.units:
                    # We have made enough room to sell the portfolio_to_sell
                    logger.info('_prepare_for_sell_order: ready to sell portfolio_to_sell {}'.format(
                        portfolio_to_sell))
                    return True

    logger.info('_prepare_for_sell_order: cancelled_orders {} not enough. Buy back sold calls portfolio_to_sell {}'
                .format(cancelled_orders, portfolio_to_sell))

    buy_back_orders = 0
    for portfolio in portfolio_list:
        watchlist = watchlists_dict[portfolio.watchlist_id]
        if watchlist.asset_type == AssetTypes.CALL_OPTION.value and portfolio.transaction_type == TransactionType.SELL.value:
            buy_back_orders += portfolio.units
            # Buyback at the ask price
            buy_back_order = order_bll.submit_market_order_to_client(
                watchlist, TransactionType.BUY.value, portfolio.units, OrderAction.CLOSE.value)
            logger.info('_prepare_for_sell_order: portfolio_to_sell {}, buy_back_order{}'.format(
                portfolio_to_sell, buy_back_order))

            if buy_back_orders > portfolio_to_sell.units:
                logger.info('_prepare_for_sell_order: prepared to sell portfolio_to_sell {}'.format(
                    portfolio_to_sell))

                # We need to wait for the orders to get executed
                return False

    return False



def _validate_strategy(strategy_type, portfolio):
    watchlist = watchlist_bll.get_watchlist(portfolio.watchlist_id)

    if strategy_type == StrategyType.COVERED_CALL.value:
        # This strategy can only be applied on sold options
        if portfolio.transaction_type != TransactionType.SELL.value\
                or watchlist.asset_type != AssetTypes.CALL_OPTION.value:
            # Covered call strategy doesnt apply here
            return False

    # TODO: Add checks for other strategies

    return True

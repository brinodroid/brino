import logging
from datetime import datetime, timedelta
from brStrategy.models import Strategy
from brStrategy.serializer import StrategySerializer
import brCore.portfolio_bll as portfolio_bll
from common.types.asset_types import AssetTypes, PortFolioSource, TransactionType


logger = logging.getLogger('django')

def create_strategy(strategy_user_request, scan_entry):
    
    serializer = StrategySerializer(data=strategy_user_request)
    if serializer.is_valid() == False:
        logger.error(serializer.errors)
        raise ValueError('Strategy serializing error:'+ serializer.errors)

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
        raise ValueError('Strategy serializing error:'+ serializer.errors)

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
        porfolio = portfolio_bll.get_portfolio(portfolio_id)
        if portfolio == None:
            logger.error("create_strategy: Cannot find portfolio_id {}".format(portfolio_id))
            raise ValueError('Strategy given invalid portfolio_id '+ str(portfolio_id))

        if 'profit_target' not in serializer.validated_data.keys():
            # User have not provided profit_target. Compute profit target
            profit_target = settings_bll.compute_profit_target(porfolio.entry_price,
                     porfolio.transaction_type)

        if 'stop_loss' in serializer.validated_data.keys():
            # User have not provided stop_loss. Compute it
            stop_loss = settings_bll.compute_stop_loss(portfolio.entry_price,
                     portfolio.transaction_type)

    if 'portfolio_id' in serializer.validated_data.keys():
        # Include portfolio_id to save
        strategy = Strategy(strategy_type=strategy_type,
                    profit_target=profit_target,
                    stop_loss=stop_loss,
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

    for active_strategy in active_strategy_list:
        portfolio = portfolio_bll.get_portfolio(active_strategy.portfolio_id)
        if portfolio is None:
            logger.info('strategy_run: Missing portfolio for {}'.format(active_strategy))
            continue

        if portfolio.transaction_type == TransactionType.BUY.value:
            _buy_strategy(active_strategy, portfolio)
        elif portfolio.transaction_type == TransactionType.SELL.value:
            _sell_strategy(active_strategy, portfolio)
        else:
            logger.error('strategy_run: Invalid trasaction type? {}'.format(portfolio.transaction_type))


    return

def _sell_strategy(strategy, portfolio):
    logger.info('_sell_strategy: strategy {}, portfolio {}'.format(strategy, porfolio))
    return

def _buy_strategy(strategy, portfolio):
    logger.info('_buy_strategy: strategy {}, portfolio {}'.format(strategy, porfolio))
    return
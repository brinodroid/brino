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
            logger.info('strategy_run: Buy strategy for {}'.format(active_strategy))
        elif portfolio.transaction_type == TransactionType.SELL.value:
            logger.info('strategy_run: Sell strategy for {}'.format(active_strategy))
        else:
            logger.error('strategy_run: Invalid trasaction type? {}'.format(portfolio.transaction_type))


    return
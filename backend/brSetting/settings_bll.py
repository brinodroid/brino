import logging
from datetime import datetime, timedelta
from brSetting.models import Configuration
from common.types.asset_types import AssetTypes, TransactionType

logger = logging.getLogger('django')

def compute_profit_target(entry_price, transaction_type):
    configuration = Configuration.objects.first()

    if transaction_type == TransactionType.BUY:
        profit_target = entry_price * \
            (100+configuration.profitTargetPercent)/100
    elif transaction_type == TransactionType.SELL:
        profit_target = entry_price * \
            (100-configuration.profitTargetPercent)/100
    else:
        logger.error('compute_profit_target: invalid transaction type {}'
                        .format(transaction_type))
        return None
    
    return profit_target


def compute_stop_loss(entry_price, transaction_type):
    configuration = Configuration.objects.first()

    if transaction_type == TransactionType.BUY:
        stop_loss = entry_price * \
            (100-configuration.stopLossPercent)/100
    elif transaction_type == TransactionType.SELL:
        stop_loss = entry_price * \
            (100+configuration.stopLossPercent)/100
    else:
        logger.error('compute_stop_loss: invalid transaction type {}'
                        .format(transaction_type))
        return None
    
    return stop_loss

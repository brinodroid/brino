import logging
from datetime import datetime, timedelta

logger = logging.getLogger('django')

option_unit_multiplier = 100.0

def safe_float(float_string):
    try:
        f = float(float_string)
        return f
    except:
        logger.info('__safe_float: Not valid number =%s', float_string)
    return 0

def safe_int(self, int_string):
    try:
        f = int(int_string)
        return f
    except:
        logger.info('__safe_int: Not valid number =%s', int_string)
    return 0
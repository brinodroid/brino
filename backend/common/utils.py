import logging
from datetime import datetime, timedelta
from django.utils.timezone import localdate
import pytz

logger = logging.getLogger('django')

option_unit_multiplier = 100.0

datetime_strpfmt_string = "%Y-%m-%dT%H:%M:%SZ"

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

def convert_datetime_string_to_django_time(datetime_string):
    try:
        date_in_datetime = datetime.strptime(datetime_string, datetime_strpfmt_string)
        awaretime = date_in_datetime.replace(tzinfo=pytz.UTC)

        local_date = localdate(awaretime)
        return local_date
    except:

        logger.info('__safe_int: Not valid number =%s', int_string)
    return None

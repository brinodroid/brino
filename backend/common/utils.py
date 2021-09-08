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
    date_in_datetime = datetime.strptime(datetime_string, datetime_strpfmt_string)
    awaretime = date_in_datetime.replace(tzinfo=pytz.UTC)

    local_date = localdate(awaretime)
    return local_date

def today_begin_utctime_string():
    today_begin_utc=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=pytz.UTC)

    #yesterday_utc = today_begin_utc - timedelta(1)
    #return yesterday_utc.strftime(datetime_strpfmt_string)

    return today_begin_utc.strftime(datetime_strpfmt_string)

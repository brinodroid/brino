import logging
from datetime import date, datetime, timedelta
import calendar
from django.utils.timezone import localdate
import pytz


logger = logging.getLogger('django')

option_unit_multiplier = 100.0
option_expiry_date_strpfmt_string = "%Y-%m-%d"

datetime_strpfmt_string = "%Y-%m-%dT%H:%M:%SZ"

def safe_float(float_string):
    try:
        f = float(float_string)
        return f
    except:
        logger.info('__safe_float: Not valid number =%s', float_string)
    return 0

def safe_int(int_string):
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

def third_friday_of_next_month():
    today = date.today()
    return third_friday_of_next_month_with_date(today)

def third_friday_of_next_month_with_date(from_date):
    next_month = date(from_date.year, from_date.month, 1) + timedelta(days=32)
    return get_coming_monthly_option(next_month)

def get_coming_monthly_option(from_date):
    third_week_of_the_month = date(from_date.year, from_date.month, 15)

    third_friday_of_the_month = third_week_of_the_month + timedelta(days=(calendar.FRIDAY - third_week_of_the_month.weekday()) % 7)

    if third_friday_of_the_month >= from_date:
        # The computed date is in the future, return it
        return third_friday_of_the_month

    # The third friday of the month is before the from_date. So the next monthly option should be in next month
    # Go to next month by adding 32 from the first of the month
    next_month = date(from_date.year, from_date.month, 1) + timedelta(days=32)

    return get_coming_monthly_option(next_month)

def get_days_to_monthly_option_expiry(from_date):
    upcoming_option_expiry = get_coming_monthly_option(from_date)

    timedelta = upcoming_option_expiry - from_date

    return timedelta.days

def get_coming_quarterly_option_expiry(from_date):
    next_quarterly_month = date(from_date.year, int((from_date.month/3 +1)*3), 1)

    upcoming_quarterly_expiry = get_coming_monthly_option(next_quarterly_month)
    if upcoming_quarterly_expiry >= from_date:
        # The computed date is in the future, return it
        return upcoming_quarterly_expiry

    # Go to next month by adding 32 from the first of the month
    next_month = date(from_date.year, from_date.month, 1) + timedelta(days=32)

    return get_coming_quarterly_option_expiry(next_month)

def get_days_to_quarterly_option_expiry(from_date):
    upcoming_quarterly_option_expiry = get_coming_quarterly_option_expiry(from_date)

    timedelta = upcoming_quarterly_option_expiry - from_date

    return timedelta.days

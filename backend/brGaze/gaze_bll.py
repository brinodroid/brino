import logging
from datetime import date, datetime, timedelta
from brCore.models import WatchList
from common.types.asset_types import AssetTypes
import brCore.watchlist_bll as watchlist_bll
import brHistory.history_bll as history_bll
import common.utils as utils
from django.utils import timezone


logger = logging.getLogger('django')


def create_closest_options(watchlist_id):
    logger.info(
        'create_closest_options: watchlist_id'.format(watchlist_id))

    watchlist = watchlist_bll.get_watchlist(watchlist_id)

    if watchlist_bll.is_option(watchlist):
        # Closest monthly option update only supported for stocks
        logger.error('create_closest_options: watchlist id is not stock, watchlist {}'
                     .format(watchlist))
        raise ValueError("Asset type expected is stock, got option")

    __create_closest_options(watchlist)

    return


def create_closest_options_for_all_stocks():
    watchlist_list = watchlist_bll.get_stock_watchlist()

    for watchlist in watchlist_list:
        logger.info(
            'create_closest_options_for_all_stocks: watchlist {}'.format(watchlist))
        __create_closest_options(watchlist)

    return


def __create_closest_options(watchlist):
    logger.info('__create_closest_options: watchlist {}'.format(watchlist))

    closing_price = watchlist_bll.get_watchlist_latest_price(
        watchlist, includeExtendedHours=False)

    # Get call option monthly expiry date after 20days beyond current date.
    next_monthly_expiry = utils.third_friday_of_next_month()

    closest_call_option_watchlist = watchlist_bll.create_watchlist_for_call_option_above_price(
        watchlist, closing_price, next_monthly_expiry)
    logger.info('__create_closest_options: closest_call_option_watchlist {}'.format(
        closest_call_option_watchlist))

    closest_put_option_watchlist = watchlist_bll.create_watchlist_for_put_option_below_price(
        watchlist, closing_price, next_monthly_expiry)
    logger.info('__create_closest_options: closest_put_option_watchlist {}'.format(
        closest_put_option_watchlist))

    return


def train_lstm(watchlist_id):
    logger.info('train_lstm: watchlist_id {}'.format(watchlist_id))
    watchlist = watchlist_bll.get_watchlist(watchlist_id)

    input_sequence = _prepare_training_data_sequence(watchlist, 7)

    return


def infer_lstm(watchlist_id):
    logger.info('infer_lstm: watchlist_id {}'.format(watchlist_id))

    ret_test = [{'10/2/2222', 10},
                {'10/3/2222', 10},
                {'10/4/2222', 10},
                {'10/5/2222', 10},
                {'10/6/2222', 10}]

    return ret_test


def _prepare_training_data_sequence(watchlist, past_days):
    training_data = []
    start_date = timezone.now().date() - timedelta(days=past_days)
    stock_history = None

    for i in range(0, past_days):
        hist_date = start_date + timedelta(days=i)
        prev_stock_history = stock_history
        stock_history = history_bll.get_history_on_date(watchlist, hist_date)
        if stock_history == None:
            # We seem to have missed data in history
            if prev_stock_history:
                stock_history = prev_stock_history

                logger.info('_prepare_training_data: REUSING previous data for date {} for watchlist {}'
                    .format(hist_date, watchlist))
            else:
                # The entry is missing

                # Try going a day back
                hist_date = hist_date - timedelta(days=1)

                stock_history = history_bll.get_history_on_date(watchlist, hist_date)
                if stock_history == None:
                    logger.error('_prepare_training_data: missing data date {} for watchlist {}. IGNORING'
                        .format(hist_date, watchlist))
                continue

        # We have stock history            
        history = _create_training_data(watchlist, stock_history, hist_date)
        training_data.append(history)

    return training_data


def _create_training_data(watchlist, stock_history, hist_date):
    history = {}

    # Date parameters
    history['date'] = stock_history.date
    history['day_of_month'] = hist_date.day
    history['week_day'] = hist_date.weekday()
    history['days_to_monthly_option_expiry'] = utils.get_days_to_monthly_option_expiry(hist_date)
    history['days_to_quarterly_option_expiry'] = utils.get_days_to_quarterly_option_expiry(hist_date)
    
    # Stock parameters
    history['high_price'] = stock_history.high_price
    history['low_price'] = stock_history.low_price
    history['open_price'] = stock_history.open_price
    history['close_price'] = stock_history.close_price
    history['volume'] = stock_history.volume
    history['average_volume_2_weeks'] = stock_history.average_volume_2_weeks
    history['average_volume'] = stock_history.average_volume
    history['dividend_yield'] = stock_history.dividend_yield
    history['market_cap'] = stock_history.market_cap
    history['pb_ratio'] = stock_history.pb_ratio
    history['pe_ratio'] = stock_history.pe_ratio

    # Low frequency changes
    history['low_52_weeks'] = stock_history.low_52_weeks
    history['high_52_weeks'] = stock_history.high_52_weeks
    history['num_employees'] = stock_history.num_employees
    history['shares_outstanding'] = stock_history.shares_outstanding
    history['float'] = stock_history.float

    monthly_expiry = utils.third_friday_of_next_month_with_date(stock_history.date)

    _add_closest_put_option_history(history, monthly_expiry, watchlist, stock_history)

    _add_closest_call_option_history(history, monthly_expiry, watchlist, stock_history)

    return history

def _add_closest_put_option_history(history, monthly_expiry, watchlist, stock_history):
    closest_put_option_watchlist = watchlist_bll.get_watchlist_closest_strike_below_price(
        AssetTypes.PUT_OPTION.value, watchlist.ticker, monthly_expiry, stock_history.close_price)

    put_option_history = history_bll.get_history_on_date(closest_put_option_watchlist, stock_history.date)

    history['put_mark_price'] = put_option_history.mark_price
    history['put_ask_price'] = put_option_history.ask_price
    history['put_bid_price'] = put_option_history.bid_price
    history['put_high_price'] = put_option_history.high_price
    history['put_low_price'] = put_option_history.low_price
    history['put_last_trade_price'] = put_option_history.last_trade_price
    history['put_open_interest'] = put_option_history.open_interest
    history['put_volume'] = put_option_history.volume
    history['put_ask_size'] = put_option_history.ask_size
    history['put_bid_size'] = put_option_history.bid_size
    history['put_delta'] = put_option_history.delta
    history['put_gamma'] = put_option_history.gamma
    history['put_implied_volatility'] = put_option_history.implied_volatility
    history['put_rho'] = put_option_history.rho
    history['put_theta'] = put_option_history.theta
    history['put_vega'] = put_option_history.vega
    
    return history


def _add_closest_call_option_history(history, monthly_expiry, watchlist, stock_history):
    closest_call_option_watchlist = watchlist_bll.get_watchlist_closest_strike_above_price(
        AssetTypes.CALL_OPTION.value, watchlist.ticker, monthly_expiry, stock_history.close_price)

    call_option_history = history_bll.get_history_on_date(closest_call_option_watchlist, stock_history.date)

    history['call_mark_price'] = call_option_history.mark_price
    history['call_ask_price'] = call_option_history.ask_price
    history['call_bid_price'] = call_option_history.bid_price
    history['call_high_price'] = call_option_history.high_price
    history['call_low_price'] = call_option_history.low_price
    history['call_last_trade_price'] = call_option_history.last_trade_price
    history['call_open_interest'] = call_option_history.open_interest
    history['call_volume'] = call_option_history.volume
    history['call_ask_size'] = call_option_history.ask_size
    history['call_bid_size'] = call_option_history.bid_size
    history['call_delta'] = call_option_history.delta
    history['call_gamma'] = call_option_history.gamma
    history['call_implied_volatility'] = call_option_history.implied_volatility
    history['call_rho'] = call_option_history.rho
    history['call_theta'] = call_option_history.theta
    history['call_vega'] = call_option_history.vega
    
    return history
import logging
from datetime import date, datetime, timedelta
from brCore.models import WatchList
from brGaze.models import NNModelStatus
from brGaze.nn.lstm import LSTM
from common.types.asset_types import AssetTypes
import brCore.watchlist_bll as watchlist_bll
import brHistory.history_bll as history_bll
import common.utils as utils
from django.utils import timezone
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import torch
from torch.autograd import Variable
import copy


logger = logging.getLogger('django')

OS_PATH_NN_DATA = 'brGaze/nn/data/'


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


def __get_nnmodel_status(watchlist_id):
    nnmodel_status = NNModelStatus.objects.filter(
        watchlist_id=int(watchlist_id))
    if nnmodel_status.exists():
        # We got history for the date
        return nnmodel_status[0]

    # No data
    return None


def train_lstm(watchlist_id):
    sequence_length = 7  # Weekly sequence
    logger.info('train_lstm: watchlist_id {}'.format(watchlist_id))
    watchlist = watchlist_bll.get_watchlist(watchlist_id)

    nnmodel_status = __get_nnmodel_status(watchlist_id)

    if nnmodel_status is None:
        # Our date is from Jan 2022
        data_start_date = date(2022, 1, 1)
    else:
        data_start_date = nnmodel_status.trained_till_date - \
            timedelta(days=sequence_length)

    training_data_list_of_maps = _prepare_training_data(
        watchlist, data_start_date, timezone.now().date())

    input_sequence = _prepare_training_data_sequence(
        watchlist, training_data_list_of_maps, 7)

    # Input size:
    # Batch size
    # timesteps

    model = LSTM()
    loss_function = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 150

    for i in range(epochs):
        for seq, labels in input_sequence:
            optimizer.zero_grad()
            model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                                 torch.zeros(1, 1, model.hidden_layer_size))

            y_pred = model(seq)

            single_loss = loss_function(y_pred, labels)
            single_loss.backward()
            optimizer.step()

        if i % 25 == 1:
            print(f'epoch: {i:3} loss: {single_loss.item():10.8f}')

    scaler_file_name = _get_default_min_max_scaler_path(watchlist)
    if os.path.exists(scaler_file_name):
        scaler = joblib.load(scaler_file_name)

    data_predict = y_pred.data.numpy() #numpy conversion

    data_predict_final = scaler.inverse_transform(data_predict)
    print(f'epoch: {i:3} loss: {single_loss.item():10.10f} data_predict: {data_predict:10.10f} data_predict_final: {data_predict_final:10.10f}')

    return


def infer_lstm(watchlist_id):
    logger.info('infer_lstm: watchlist_id {}'.format(watchlist_id))

    ret_test = [{'10/2/2222', 10},
                {'10/3/2222', 10},
                {'10/4/2222', 10},
                {'10/5/2222', 10},
                {'10/6/2222', 10}]

    return ret_test


def _get_default_min_max_scaler_path(watchlist):
    dir_name = OS_PATH_NN_DATA + watchlist.ticker
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    scaler_file_name = dir_name + '/default_min_max_scaler.gz'
    return scaler_file_name


def _prepare_training_data_sequence(watchlist, training_data_list_of_maps, past_days):

    training_data_list = []
    for training_data_map in training_data_list_of_maps:
        training_data_map.pop('date')
        training_data = list(training_data_map.values())
        training_data_list.append(training_data)

    scaler_file_name = _get_default_min_max_scaler_path(watchlist)
    if os.path.exists(scaler_file_name):
        scaler = joblib.load(scaler_file_name)
    else:
        scaler = MinMaxScaler()

    training_data_normalized = scaler.fit_transform(training_data_list)
    joblib.dump(scaler, scaler_file_name)

    X_train_tensors = Variable(torch.Tensor(training_data_normalized))
    shape = X_train_tensors.shape

    X_train_tensors_final = torch.reshape(X_train_tensors,   (X_train_tensors.shape[0], 1, X_train_tensors.shape[1]))
    shape1 = X_train_tensors_final.shape

    training_data_normalized_tensors = torch.FloatTensor(
        training_data_normalized).view(-1)

    x = training_data_normalized_tensors.shape
    training_data_sequence = _create_sequences(
        training_data_normalized_tensors, past_days)

    return training_data_sequence


def _create_sequences(input_data, window):
    inout_seq = []
    L = len(input_data)
    for i in range(L-window):
        train_seq = input_data[i:i+window]
        train_label = input_data[i+window:i+window+1]
        inout_seq.append((train_seq, train_label))
    return inout_seq


def _prepare_training_data(watchlist, start_date, end_date):
    training_data = []

    stock_history_sorted_list = history_bll.get_history(
        watchlist, start_date, end_date)
    stock_hist_expected_date = start_date

    call_option_history = None
    put_option_history = None
    prev_put_option_history = None
    prev_call_option_history = None

    for stock_history in stock_history_sorted_list:
        stock_hist_expected_date = stock_hist_expected_date + timedelta(days=1)

        if stock_history.date < stock_hist_expected_date:
            # We seem to have data from dates before expected dates. Duplicate data??
            logger.error('_prepare_training_data: SKIPPING mismatched for watchlist {}, expecting {}, got {}'
                         .format(watchlist, stock_hist_expected_date, stock_history.date))
            continue

        while stock_history.date > stock_hist_expected_date:
            # We seem to have missed data in history. Take previous data if it exists
            missed_date = stock_hist_expected_date
            stock_hist_expected_date = stock_hist_expected_date + \
                timedelta(days=1)

            if len(training_data):
                logger.info('_prepare_training_data: REUSING previous data for date {} for watchlist {}'
                            .format(missed_date, watchlist))

                # Get previous data
                prev_training_data = copy.deepcopy(training_data[-1])

                # Update date parameters
                _update_date_params(prev_training_data, missed_date)

                # Add the missing data
                training_data.append(prev_training_data)
            else:
                logger.error('_prepare_training_data: SKIPPING No prev_training_data for date {} for watchlist {}'
                             .format(missed_date, watchlist))

        # We have the right date
        monthly_expiry = utils.third_friday_of_next_month_with_date(
            stock_history.date)

        prev_put_option_history = put_option_history
        # Get the closest put option history
        put_option_history = __get_put_option_history(
            watchlist, stock_history, monthly_expiry)
        if put_option_history is None:
            put_option_history = prev_put_option_history

        if put_option_history is None:
            # We do not have even previous valid data to continue
            logger.error('_prepare_training_data: SKIPPING No put_option_history for date {} for watchlist {}'
                         .format(stock_hist_expected_date, watchlist))

        prev_call_option_history = call_option_history
        # Get the closest call option history
        call_option_history = __get_call_option_history(
            watchlist, stock_history, monthly_expiry)
        if call_option_history is None:
            call_option_history = prev_call_option_history

        if call_option_history is None:
            # We do not have even previous valid data to continue
            logger.error('_prepare_training_data: SKIPPING No call_option_history for date {} for watchlist {}'
                         .format(stock_hist_expected_date, watchlist))

        if put_option_history and call_option_history:
            # We have valid data, use it
            history = _create_training_data(
                watchlist, stock_history, call_option_history, put_option_history, stock_hist_expected_date)
            training_data.append(history)

    return training_data


def __get_put_option_history(watchlist, stock_history, monthly_expiry):
    closest_put_option_watchlists_sorted_desc = watchlist_bll.get_watchlists_closest_strike_below_price(
        AssetTypes.PUT_OPTION.value, watchlist.ticker, monthly_expiry, stock_history.close_price)
    if not closest_put_option_watchlists_sorted_desc.exists():
        logger.error('__get_put_option_history: No closest option found for date {} for watchlist {}'
                     .format(monthly_expiry, watchlist))
        return None

    # we have a valid watch list
    for put_option_watchlist in closest_put_option_watchlists_sorted_desc:
        # Loop through to find the history
        put_option_history = history_bll.get_history_on_date(
            put_option_watchlist, stock_history.date)
        if put_option_history is not None:
            return put_option_history

    # No history available
    return None

def __get_call_option_history(watchlist, stock_history, monthly_expiry):
    closest_call_option_watchlists = watchlist_bll.get_watchlists_closest_strike_above_price(
        AssetTypes.CALL_OPTION.value, watchlist.ticker, monthly_expiry, stock_history.close_price)

    if not closest_call_option_watchlists.exists():
        logger.error('__get_call_option_history: No closest option found for date {} for watchlist {}'
                     .format(monthly_expiry, watchlist))
        return None

    # we have a valid watch list
    for call_option_watchlist in closest_call_option_watchlists:
        # Loop through to find the history
        call_option_history = history_bll.get_history_on_date(
            call_option_watchlist, stock_history.date)

        if call_option_history is not None:
            return call_option_history

    # No history available
    return None


def _create_training_data(watchlist, stock_history, call_option_history, put_option_history, hist_date):
    history = {}

    # Date parameters
    _update_date_params(history, hist_date)

    history['date'] = stock_history.date
    history['day_of_month'] = hist_date.day
    history['week_day'] = hist_date.weekday()
    history['days_to_monthly_option_expiry'] = utils.get_days_to_monthly_option_expiry(
        hist_date)
    history['days_to_quarterly_option_expiry'] = utils.get_days_to_quarterly_option_expiry(
        hist_date)

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

    _update_put_option_params(
        history, put_option_history)

    _update_call_option_params(
        history, call_option_history)

    return history


def _update_date_params(history, hist_date):
    # Date parameters
    history['date'] = hist_date
    history['day_of_month'] = hist_date.day
    history['week_day'] = hist_date.weekday()
    history['days_to_monthly_option_expiry'] = utils.get_days_to_monthly_option_expiry(
        hist_date)
    history['days_to_quarterly_option_expiry'] = utils.get_days_to_quarterly_option_expiry(
        hist_date)


def _update_put_option_params(history, put_option_history):
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


def _update_call_option_params(history, call_option_history):
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

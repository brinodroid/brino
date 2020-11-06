import time
import brine
import json
from brCore.types.bgtask_types import BGTaskAction,  BGTaskActionResult, BGTaskStatus
from brCore.types.asset_types import AssetTypes

def __sell(watchlist, portfolio, details):
    if portfolio.units <= 0:
        print('__sell : No more units to sell', watchlist.ticker)
        return False

    # Saving the units in portfolio to avoid double selling
    units = portfolio.units
    portfolio.units = 0
    portfolio.save()
    details["sold"] = True

    print('__sell : ticker: ', watchlist.ticker, ' units: ', units)
    #brine.order_sell_market(watchlist.ticker, units)
    return

def __do_nothing(bgtask, watchlist, portfolio):
    print('__do_nothing called')
    return bgtask


def __get_detail_json(bgtask):
    print('__get_detail_json: called')
    try:
        detail_json  = json.load(bgtask.detail)
        return detail_json
    except:
      print('__get_detail_json: got exception')

    return None


def __do_stoploss_executor(bgtask, watchlist, portfolio):
    print('__do_stoploss_executor: called')
    print(time.ctime())
    assert(watchlist)
    print(bgtask)
    print(portfolio)
    print(watchlist)

    try:
        price = brine.get_latest_price(watchlist.ticker)
        print('price:', price)

        details = {"CP": float(price[0]), "SL": portfolio.stopLoss}
        if float(price[0]) < portfolio.stopLoss:
            # We need to sell it
            bgtask.actionResult = BGTaskActionResult.BAD.value
            if portfolio.units > 0:
                __sell(watchlist, portfolio, details)
        else:
            bgtask.actionResult = BGTaskActionResult.GOOD.value

        if details["sold"]:
            print('sold :', watchlist.ticker)
            bgtask.status = BGTaskStatus.PASS.value

        bgtask.details = json.dumps(details)
        print('__do_stoploss_executor: Updating:', bgtask)

    except:
        print('__do_stoploss_executor: got exception:', bgtask)

    return bgtask

def __do_stats_executor(bgtask, watchlist, portfolio):
    print('__do_stats_executor: called')
    try:
        stock_price = brine.get_latest_price(watchlist.ticker)
        stock_price_f = float(stock_price[0])
        price_f = stock_price_f

        prev_detail = __get_detail_json(bgtask)
        stock_peak_f = 1 #Cannot be 0 as we are using it in division
        if prev_detail and prev_detail['peakStock']:
            print('__do_stats_executor: prev_detail ', prev_detail)
            stock_peak_f = float(prev_detail['peakStock'])

        stock_peak_f = max(stock_peak_f, stock_price_f)
        stock_drop_from_peak_percentage =  100*(1-stock_price_f/stock_peak_f)

        if watchlist.assetType == AssetTypes.OPTION.value:
            print('__do_stats_executor: get option price. watchlist=', watchlist)
            option_data = brine.options.get_option_market_data(watchlist.ticker,
                str(watchlist.optionExpiry), str(watchlist.optionStrike), 'call')
            print(option_data)
            option_price_f = float(option_data[0][0]['mark_price'])
            price_f = option_price_f
            option_peak_f = 1
            if prev_detail and prev_detail['peakOption']:
                option_peak_f = float(prev_detail['peakOption'])
            option_peak_f = max(option_peak_f, option_price_f)
            option_drop_from_peak_percentage =  100*(1-option_price_f/option_peak_f)

        recommend = ''
        if price_f < portfolio.stopLoss:
            recommend += 'Sell as price below stopLoss. '
            bgtask.actionResult = BGTaskActionResult.BAD.value

        if price_f > portfolio.profitTarget:
            recommend += 'Sell as price above profitTarget. '

        details = {}
        #Odering the details in terms of importance
        if recommend:
          details["recommend"] = recommend

        if watchlist.assetType == AssetTypes.OPTION.value:
            details['dropFromPeakOption%'] = option_drop_from_peak_percentage
            details['CPOption'] = option_price_f
            details['peakOption'] = option_price_f

        details['dropFromPeakStock%'] = stock_drop_from_peak_percentage
        details['CPStock'] = stock_price_f
        details['peakStock'] = stock_peak_f

        bgtask.details = json.dumps(details)
        bgtask.actionResult = BGTaskActionResult.GOOD.value

    except:
        print('__do_stats_executor: got exception:', bgtask)

    return bgtask

# List of supported actions
action_list = {
    BGTaskAction.NONE.value: __do_nothing,
    BGTaskAction.STOPLOSS_EXEC.value: __do_stoploss_executor,
    BGTaskAction.COMPUTE_STATS.value: __do_stats_executor
}


def base_action(bgtask, watchlist, portfolio):
    return action_list.get(bgtask.action, "Unsupported action")(bgtask, watchlist, portfolio)

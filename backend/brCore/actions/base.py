import time
import brine
import json
import logging
import traceback
from brCore.types.bgtask_types import BGTaskAction,  BGTaskActionResult, BGTaskStatus
from brCore.types.asset_types import AssetTypes

logger = logging.getLogger('django')

def __sell(watchlist, portfolio, details):
    if portfolio.units <= 0:
        logger.error('__sell : No more units to sell for ticker %s', watchlist.ticker)
        return False

    # Saving the units in portfolio to avoid double selling
    units = portfolio.units
    portfolio.units = 0
    portfolio.save()
    details["sold"] = True

    logger.info('__sell : ticker: %s units: %d', watchlist.ticker, units)
    #brine.order_sell_market(watchlist.ticker, units)
    return

def __do_nothing(bgtask, watchlist, portfolio):
    logger.error('__do_nothing called, nothing to be done')
    return bgtask


def __get_detail_json(bgtask):
    logger.info('__get_detail_json: called: %s', bgtask.details)
    try:
        detail_json = None
        if bgtask.details:
          detail_json  = json.loads(bgtask.details)

        return detail_json

    except JSONDecodeError as e:
      logger.error('__get_detail_json: got jsonexception %s', e)
    # do whatever you want
    except TypeError as e:
      logger.error('__get_detail_json: got typeexception %s', e)
    # do whatever you want in this caseturn None


def __do_stoploss_executor(bgtask, watchlist, portfolio):
    logger.info('__do_stoploss_executor: called')

    try:
        price = brine.get_latest_price(watchlist.ticker)

        details = {"CP": float(price[0]), "SL": portfolio.stopLoss}
        if float(price[0]) < portfolio.stopLoss:
            # We need to sell it
            bgtask.actionResult = BGTaskActionResult.BAD.value
            if portfolio.units > 0:
                __sell(watchlist, portfolio, details)
        else:
            bgtask.actionResult = BGTaskActionResult.GOOD.value

        if details["sold"]:
            logger.info('sold :', watchlist.ticker)
            bgtask.status = BGTaskStatus.PASS.value

        bgtask.details = json.dumps(details)
        logger.info('__do_stoploss_executor: Updating:%s', bgtask)

    except:
        logger.error('__do_stoploss_executor: got exception:%s', bgtask)

    return bgtask

def __do_stats_executor(bgtask, watchlist, portfolio):
    logger.info('__do_stats_executor: called')
    try:
        stock_price = brine.get_latest_price(watchlist.ticker)
        stock_price_f = float(stock_price[0])
        price_f = stock_price_f

        prev_detail = __get_detail_json(bgtask)
        stock_peak_f = 1 #Cannot be 0 as we are using it in division
        if prev_detail != None and prev_detail['stockPeak']:
            logger.info('__do_stats_executor: prev_detail=%s', prev_detail)
            stock_peak_f = float(prev_detail['stockPeak'])

        stock_peak_f = max(stock_peak_f, stock_price_f)
        stock_drop_from_peak_percentage =  100*(1-stock_price_f/stock_peak_f)

        if watchlist.assetType == AssetTypes.OPTION.value:
            logger.info('__do_stats_executor: get option price. watchlist=%s', watchlist)
            option_data = brine.options.get_option_market_data(watchlist.ticker,
                str(watchlist.optionExpiry), str(watchlist.optionStrike), 'call')
            option_price_f = float(option_data[0][0]['mark_price'])
            price_f = option_price_f
            option_peak_f = 1
            if prev_detail != None and prev_detail['optPeak']:
                option_peak_f = float(prev_detail['optPeak'])
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
            details['optPeakFallPercent'] = round(option_drop_from_peak_percentage, 2)
            details['optPrice'] = option_price_f
            details['optPeak'] = option_price_f

        details['stockPeakFallPercent'] = round(stock_drop_from_peak_percentage, 2)
        details['stockPrice'] = stock_price_f
        details['stockPeak'] = stock_peak_f

        bgtask.details = json.dumps(details)
        logger.info('__do_stats_executor: setting details to: %s', bgtask.details)
        bgtask.actionResult = BGTaskActionResult.GOOD.value

    except:
        logger.error('__do_stats_executor: got exception: %s', bgtask)
        traceback.print_stack()

    return bgtask

# List of supported actions
action_list = {
    BGTaskAction.NONE.value: __do_nothing,
    BGTaskAction.STOPLOSS_EXEC.value: __do_stoploss_executor,
    BGTaskAction.COMPUTE_STATS.value: __do_stats_executor
}


def base_action(bgtask, watchlist, portfolio):
    return action_list.get(bgtask.action, "Unsupported action")(bgtask, watchlist, portfolio)

from brCore.types.bgtask_types import BGTaskAction,  BGTaskActionResult, BGTaskStatus
import time
import brine
import json

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
    brine.order_sell_market(watchlist.ticker, units)
    return

def __do_nothing(bgtask, watchlist, portfolio):
    print('__do_nothing called')
    return bgtask


def __do_test(bgtask, watchlist, portfolio):
    print('__do_test: called')
    return bgtask


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
        print('__do_stoploss_executor: get_latest_price failed :', bgtask)

    return bgtask


# List of supported actions
action_list = {
    BGTaskAction.NONE.value: __do_nothing,
    BGTaskAction.STOPLOSS_EXEC.value: __do_stoploss_executor
}


def base_action(bgtask, watchlist, portfolio):
    return action_list.get(bgtask.action, "Unsupported action")(bgtask, watchlist, portfolio)

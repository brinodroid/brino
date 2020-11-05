from brCore.utils.bgtask_types import BGTaskAction, BGTaskActionResult
import time
import brine
import json


def __do_nothing(bgtask, watchlist, portfolio):
    print('__do_nothing called')
    return bgtask


def __do_test(bgtask, watchlist, portfolio):
    print('__do_test: called')
    return bgtask


def __do_stoploss_executor(bgtask, watchlist, portfolio):
    print('__do_stoploss_executor: called')
    print(time.ctime())
    print(bgtask)
    print(portfolio)
    print(watchlist)

    try:
        price = brine.get_latest_price(watchlist.ticker)
        print('price:', price)
        if float(price[0]) < portfolio.stopLoss:
            bgtask.actionResult = BGTaskActionResult.BAD.value
        else:
            bgtask.actionResult = BGTaskActionResult.GOOD.value

        details = {"CP": float(price[0]), "SL": portfolio.stopLoss}
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

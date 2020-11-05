import threading
from .models import BGTask, WatchList, PortFolio
from .utils.bgtask_types import BGTaskAction, BGTaskStatus, BGTaskDataIdType, BGTaskActionResult
import time
import brine
import json

def __bgtask_get_portfolio(portFolioId):
    try:
      portfolio = PortFolio.objects.get(pk=portFolioId)
      print(portfolio)
      return portfolio;
    except PortFolio.DoesNotExist:
      print('__bgtask_get_portfolio: Portfolio not found', portFolioId)
      return None;

def __bgtask_get_watchlist(watchListId):
    try:
      watchlist = WatchList.objects.get(pk=watchListId)
      return watchlist
    except WatchList.DoesNotExist:
      print('__bgtask_get_watchlist: WatchList not found', watchListId)
      return None;

def __bgtask_stoploss_cc_tracker(bgtask):
    print(time.ctime())
    if bgtask.dataIdType != BGTaskDataIdType.PORTFOLIO.value:
      print('__bgtask_stoploss_cc_tracker: This action is only supported for portFolios', bgtask)
      return False

    portfolio = __bgtask_get_portfolio(bgtask.dataId)
    if portfolio == None:
      print('__bgtask_stoploss_cc_tracker: Cannot get portFolio for bgtask ', bgtask)
      return False

    watchlist = __bgtask_get_watchlist(portfolio.watchListId)
    if portfolio == None:
      print('__bgtask_stoploss_cc_tracker: Cannot get watchList from', portfolio, ' bgtask ', bgtask)
      return False

    print(watchlist)
    # TODO: do operation
    try:
        price = brine.get_latest_price(watchlist.ticker)
        print('price:', price)
        if float(price[0]) < portfolio.stopLoss:
          bgtask.actionResult = BGTaskActionResult.BAD.value
        else:
          bgtask.actionResult = BGTaskActionResult.GOOD.value

        details = {"CP" : float(price[0]), "SL": portfolio.stopLoss}
        bgtask.details = json.dumps(details)
        print('__bgtask_stoploss_cc_tracker: Updating:', bgtask)
        bgtask.save();

    except:
        print('__bgtask_stoploss_cc_tracker: get_latest_price failed :', bgtask)

    return True;


def __bgtask_stop(bgtask, status):
    bgtask.status = status
    bgtask.action = BGTaskAction.NONE.value;
    bgtask.save()

# TODO: At application start, we need to run all INPROGRESS tasks
def __bgtask_runner(bgtask_id):
    #Find a good place for login
    brine.login()
    while (True):
        try:
            bgtask = BGTask.objects.get(pk=bgtask_id)
        except BGTask.DoesNotExist:
            print('__bgtask_running: stopping bgtask as task not found, id:', bgtask_id)
            return

        if (bgtask.action == BGTaskAction.NONE.value):
            print('__bgtask_running: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            # Reset the status
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        if (bgtask.status != BGTaskStatus.RUNNING.value):
            print('__bgtask_running: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        print(bgtask);
        if __bgtask_stoploss_cc_tracker(bgtask) == False:
          print('bgtask failed', bgtask)
          __bgtask_stop(bgtask, BGTaskStatus.FAIL.value)
          return;

        time.sleep(60)


def __bgtask_thread_start(bgtask):
    t = threading.Thread(target=__bgtask_runner,
                         args=[bgtask.id])
    t.setDaemon(True)
    # Mark the task as running before starting thread
    print('Starting thread ', bgtask)
    bgtask.status = BGTaskStatus.RUNNING.value;
    bgtask.save()
    t.start()

def start_bgtask(bgtask):
    if bgtask.status != BGTaskAction.NONE.value:
        print('Starting bgtask:', bgtask)
        __bgtask_thread_start(bgtask)
    return bgtask

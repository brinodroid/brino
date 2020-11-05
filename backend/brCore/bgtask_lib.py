import threading
from .models import BGTask, WatchList, PortFolio
from .utils.bgtask_types import BGTaskAction, BGTaskStatus, BGTaskDataIdType, BGTaskActionResult
import time
import brine
import json
import sys
import traceback
from .actions.base import base_action


def __bgtask_get_portfolio(bgtask):
    if bgtask.dataIdType != BGTaskDataIdType.PORTFOLIO.value:
        print('__bgtask_get_portfolio: Not portFolio dataId', bgtask)
        return None

    # May throw exceptions which will be caught at top level run thread
    portfolio = PortFolio.objects.get(pk=bgtask.dataId)
    return portfolio


def __bgtask_get_watchlist(bgtask, portfolio):
    watchListId = bgtask.dataId
    if bgtask.dataIdType == BGTaskDataIdType.PORTFOLIO.value:
        assert (portfolio)
        watchListId = portfolio.watchListId

    try:
        watchlist = WatchList.objects.get(pk=watchListId)
        return watchlist
    except WatchList.DoesNotExist:
        print('__bgtask_get_watchlist: WatchList not found', watchListId)
        return None;


def __bgtask_stop(bgtask, status):
    bgtask.status = status
    bgtask.action = BGTaskAction.NONE.value;
    bgtask.save()


# TODO: At application start, we need to run all INPROGRESS tasks
def __bgtask_runner(bgtask_id):
    # TODO: Find a good place for login
    brine.login()
    while True:
        try:
            bgtask = BGTask.objects.get(pk=bgtask_id)
        except BGTask.DoesNotExist:
            print('__bgtask_runner: stopping bgtask as task not found, id:', bgtask_id)
            return

        if bgtask.action == BGTaskAction.NONE.value:
            print('__bgtask_runner: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            # Reset the status
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        if bgtask.status != BGTaskStatus.RUNNING.value:
            print('__bgtask_runner: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        try:
            portfolio = __bgtask_get_portfolio(bgtask)
            if portfolio is None:
                print('__bgtask_runner: Is not portfolio', bgtask)

            watchList = __bgtask_get_watchlist(bgtask, portfolio)
            if watchList is None:
                print('__bgtask_runner: Cannot get watchList from', portfolio, ' bgtask ', bgtask)
                __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
                return

            print(bgtask)
            print(portfolio)
            print(watchList)
            base_action(bgtask, watchList, portfolio)

        except BaseException as error:
            # Catch all exceptions
            __bgtask_stop(bgtask, BGTaskStatus.FAIL.value)
            e = sys.exc_info()[0]
            print("__bgtask_runner: caught  exception", error)

            # Stop the thread
            return;

        # Save the values
        bgtask.save()
        # Repeat the loop after 1min
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

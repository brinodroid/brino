import threading
from brCore.models import BGTask, WatchList, PortFolio
from brCore.types.bgtask_types import BGTaskAction, BGTaskStatus, BGTaskDataIdType
import time
import brine
import logging
import sys
from .base import base_action

logger = logging.getLogger(__name__)

def __bgtask_get_portfolio(bgtask):
    if bgtask.dataIdType != BGTaskDataIdType.PORTFOLIO.value:
        logger.error('__bgtask_get_portfolio: Not portFolio dataId %s', bgtask)
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
        logger.error('__bgtask_get_watchlist: WatchList not found %d', watchListId)
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
            logger.error('__bgtask_runner: stopping bgtask as task not found bgtask_id: %d', bgtask_id)
            return

        if bgtask.action == BGTaskAction.NONE.value:
            logger.info('__bgtask_runner: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            # Reset the status
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        if bgtask.status != BGTaskStatus.RUNNING.value:
            logger.info('__bgtask_runner: stopping bgtask as its not RUNNING state, in %s' % str(bgtask.status))
            __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
            return

        try:
            portfolio = __bgtask_get_portfolio(bgtask)
            if portfolio is None:
                logger.info('__bgtask_runner: Is not portfolio %s', bgtask)

            watchList = __bgtask_get_watchlist(bgtask, portfolio)
            if watchList is None:
                logger.error('__bgtask_runner: Cannot get watchList portfolio=%s bgtask=%s', portfolio, bgtask)
                __bgtask_stop(bgtask, BGTaskStatus.IDLE.value)
                return

            logger.info(bgtask)
            logger.info(portfolio)
            logger.info(watchList)
            base_action(bgtask, watchList, portfolio)

        except BaseException as error:
            # Catch all exceptions
            __bgtask_stop(bgtask, BGTaskStatus.FAIL.value)
            e = sys.exc_info()[0]
            logger.error("__bgtask_runner: caught  exception %s", error)

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
    logger.info('Starting thread for %s', bgtask)
    bgtask.status = BGTaskStatus.RUNNING.value;
    bgtask.save()
    t.start()


def start_bgtask(bgtask):
    if bgtask.status != BGTaskAction.NONE.value:
        logger.info('Starting bgtask: %s', bgtask)
        __bgtask_thread_start(bgtask)
    return bgtask

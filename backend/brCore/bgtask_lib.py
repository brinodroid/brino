import threading
from .models import BGTask, WatchList
from .utils.bgtask_status import BGTaskStatus
from .utils.bgtask_action import BGTaskAction
import time

def __bgtask_stoploss_cc_tracker(bgtask, watchlist):
    # compute stop loss value
    # current price - cc value is < stop loss value, mark it as bad
    print(watchlist)
    print(time.ctime())
    # TODO: do operation
    try:
        price = 10
        print('price:', price)
    except:
        print('__bgtask_stoploss_cc_tracker: get_latest_price failed :', bgtask)

    return;


def __bgtask_stop(bgtask, status):
    bgtask.status = status
    bgtask.save()

# TODO: At application start, we need to run all INPROGRESS tasks
def __bgtask_runner(bgtask_id):
    while (True):
        try:
            bgtask = BGTask.objects.get(pk=bgtask_id)
        except BGTask.DoesNotExist:
            print('__bgtask_running: stopping bgtask as task not found, id:', bgtask_id)
            return

        if (bgtask.status != BGTaskStatus.IN_PROGRESS.value):
            print('__bgtask_running: stopping bgtask as its not in INPROGRESS: %s' % str(bgtask.status))
            return

        print(bgtask.status)
        try:
            watchlist = WatchList.objects.get(pk=bgtask.watchListId)
        except WatchList.DoesNotExist:
            print('__bgtask_running: stopping bgtask as task not found, id:', bgtask_id)
            __bgtask_stop(bgtask, BGTaskStatus.FAIL.value)
            return

        __bgtask_stoploss_cc_tracker(bgtask, watchlist)
        time.sleep(60)


def __bgtask_thread_start(bgtask):
    t = threading.Thread(target=__bgtask_runner,
                         args=[bgtask.id])
    t.setDaemon(True)
    # Mark the task as running before starting thread
    t.start()

def start_bgtask(bgtask):
    if bgtask.status != BGTaskAction.NO_ACTION.value:
        print('Starting bgtask:', bgtask)
        __bgtask_thread_start(bgtask)
    return bgtask

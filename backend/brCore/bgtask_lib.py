import threading
from .models import WatchList, BGTask
from .utils.bgtask_status import BGTaskStatus
from .utils.bgtask_action import BGTaskAction
import time


#TODO: At application start, we need to run all INPROGRESS tasks
def __bgtask_runner(bgtask_id):
    while (True):
        try:
            bgtask = BGTask.objects.get(pk=bgtask_id)
        except BGTask.DoesNotExist:
            print('__bgtask_running: stopping bgtask as task not found, id:', bgtask_id)
            return;

        print(bgtask)
        print(time.ctime())
        # TODO: do operation
        time.sleep(10)


def start_bgtask(bgtask):
    t = threading.Thread(target=__bgtask_runner,
                         args=[bgtask.id])
    t.setDaemon(True)
    # Mark the task as running before starting thread
    bgtask.status = BGTaskStatus.IN_PROGRESS.value
    bgtask.save()
    t.start()
    return bgtask

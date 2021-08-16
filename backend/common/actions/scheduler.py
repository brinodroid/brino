import threading
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from common.actions.scanner import Scanner
from brHistory.crawler import Crawler
import brStrategy.strategy_bll as strategy_bll

from django.utils import timezone

import brOrder.order_bll as order_bll

logger = logging.getLogger('django')


def _daily_weekday_10pm_task():
    logger.info('_daily_weekday_10pm_task: starting {}'.format(timezone.now()))

    try:
        Scanner.getInstance().get_lock().acquire()

        order_bll.poll_order_status()
        Crawler.getInstance().save_history()
    finally:
        Scanner.getInstance().get_lock().release()

    logger.info('_daily_weekday_10pm_task: ending {}'.format(timezone.now()))
    return

def _one_minute_task():
    logger.info('_one_minute_task: starting {}'.format(timezone.now()))

   # _daily_weekday_10pm_task()

    try:
        Scanner.getInstance().get_lock().acquire()
        strategy_bll.strategy_run()
    finally:
        Scanner.getInstance().get_lock().release()

    logger.info('_one_minute_task: ending {}'.format(timezone.now()))
    return


def _five_minute_task():
    logger.info('_five_minute_task: starting {}'.format(timezone.now()))

    try:
        Scanner.getInstance().get_lock().acquire()
        Scanner.getInstance().scan()
    finally:
        Scanner.getInstance().get_lock().release()

    logger.info('_five_minute_task: ending {}'.format(timezone.now()))
    return


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # Run the job Monday to Friday 5am IST which is 10pm PDT
    scheduler.add_job(_daily_weekday_10pm_task, 'cron', day_of_week='mon-fri', hour=5, id='daily_weekday_10pm_task', jobstore='default', replace_existing=True)

    scheduler.add_job(_one_minute_task, 'interval', minutes=1, id='one_minute_task', jobstore='default', replace_existing=True)
    scheduler.add_job(_five_minute_task, 'interval', minutes=5, id='five_minute_task', jobstore='default', replace_existing=True)

    register_events(scheduler)
    scheduler.start()

    logger.info('BackgroundScheduler started')



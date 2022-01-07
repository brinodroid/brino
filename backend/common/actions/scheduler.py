import threading
import time
import traceback
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from common.actions.scanner import Scanner
from common.actions.pf_update import PFUpdater
import brStrategy.strategy_bll as strategy_bll
import brHistory.history_bll as history_bll
import brGaze.gaze_bll as gaze_bll

from django.utils import timezone

import brOrder.order_bll as order_bll

logger = logging.getLogger('django')


def _daily_weekday_10pm_task():
    logger.info('_daily_weekday_10pm_task: starting {}'.format(timezone.now()))

    try:
        Scanner.getInstance().get_lock().acquire()

        order_bll.poll_order_status()

        # Need to capture the closest option history
        gaze_bll.create_closest_options_for_all_stocks()

        # Capture history
        history_bll.save_history()

        #Take a backup of the db
        ret = os.system('cp db.sqlite3 /tmp/db.sqlite3; rclone copy /tmp/db.sqlite3 gdrive:brino_backup/; rm /tmp/db.sqlite3;')
        logger.info('_daily_weekday_10pm_task: db backup gave  {}'.format(ret))

    except:
        logger.error('_daily_weekday_10pm_task: caught exception'.format(traceback.format_exc()))

    Scanner.getInstance().get_lock().release()

    logger.info('_daily_weekday_10pm_task: ending {}'.format(timezone.now()))
    return

def _minute_task():
    logger.info('_minute_task: starting {}'.format(timezone.now()))


    # _daily_weekday_10pm_task()

    # _hourly_task()

    try:
        Scanner.getInstance().get_lock().acquire()

        strategy_bll.strategy_run()
    except:
        logger.error('_minute_task: caught exception'.format(traceback.format_exc()))

    Scanner.getInstance().get_lock().release()

    logger.info('_minute_task: ending {}'.format(timezone.now()))
    return


def _hourly_task():
    logger.info('_hourly_task: starting {}'.format(timezone.now()))
    # Changing to run it ondemand
    # Scanner.getInstance().scan()

    logger.info('_hourly_task: ending {}'.format(timezone.now()))
    return

def _5pm_daily_task():
    logger.info('_5pm_daily_task: starting {}'.format(timezone.now()))

    try:
        Scanner.getInstance().get_lock().acquire()

        PFUpdater.getInstance().update('BRINE')
        logger.info('_5pm_daily_task: done with update {}'.format(timezone.now()))
    finally:
        Scanner.getInstance().get_lock().release()

    logger.info('_5pm_daily_task: start scanning {}'.format(timezone.now()))
    # Scan takes the lock internally
    Scanner.getInstance().scan()

    logger.info('_5pm_daily_task: ending {}'.format(timezone.now()))
    return

def _5am_daily_task():
    logger.info('_5am_daily_task: starting {}'.format(timezone.now()))

    try:
        Scanner.getInstance().get_lock().acquire()

        PFUpdater.getInstance().update('BRINE')
        logger.info('_5am_daily_task: done with update {}'.format(timezone.now()))
    finally:
        Scanner.getInstance().get_lock().release()

    logger.info('_5am_daily_task: start scanning {}'.format(timezone.now()))
    # Scan takes the lock internally
    Scanner.getInstance().scan()

    logger.info('_5am_daily_task: ending {}'.format(timezone.now()))
    return


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Run the job Monday to Saturday 5am GMT which is 10pm PDT
    scheduler.add_job(_daily_weekday_10pm_task, 'cron', day_of_week='mon-sat', hour=5, id='daily_weekday_10pm_task', jobstore='default', replace_existing=True)
    # Run the job Monday to Saturday 1am GMT which is 5pm PST
    scheduler.add_job(_5pm_daily_task, 'cron', day_of_week='mon-sun', hour=1, id='5pm_daily_task', jobstore='default', replace_existing=True)
    # Run the job Monday to Saturday 1pm GMT which is 5am PST
    scheduler.add_job(_5am_daily_task, 'cron', day_of_week='mon-sun', hour=13, id='5am_daily_task', jobstore='default', replace_existing=True)

    scheduler.add_job(_minute_task, 'interval', minutes=1, id='minute_task', jobstore='default', replace_existing=True)
    scheduler.add_job(_hourly_task, 'interval', minutes=60, id='hourly_task', jobstore='default', replace_existing=True)

    register_events(scheduler)
    scheduler.start()

    logger.info('BackgroundScheduler started')



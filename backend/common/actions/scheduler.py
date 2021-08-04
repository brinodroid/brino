import threading
import time
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import brOrder.order_bll as order_bll
from django.utils import timezone

logger = logging.getLogger('django')


def daily_10pm_task():
    logger.info('daily_10pm_task: {}'.format(timezone.now()))
    order_bll.poll_order_status()
    logger.info('daily_10pm_task:')
    return


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # Run the job Monday to Friday 5am IST which is 10pm PDT
    scheduler.add_job(daily_10pm_task, 'cron', day_of_week='mon-fri', hour=5, id='daily_10pm_task', jobstore='default', replace_existing=True)

    register_events(scheduler)
    scheduler.start()

    logger.info('BackgroundScheduler started')

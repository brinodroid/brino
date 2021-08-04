"""
WSGI config for skel project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
from common.actions.scanner import Scanner
import common.actions.scheduler as scheduler

from brHistory.crawler import Crawler

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skel.settings')

application = get_wsgi_application()

Scanner.getInstance().start()
Crawler.getInstance().start()

scheduler.start()

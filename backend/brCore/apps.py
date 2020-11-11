from django.apps import AppConfig
import logging


class BrcoreConfig(AppConfig):
    name = 'brCore'
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    def ready(self):
        print('brcore ready called')


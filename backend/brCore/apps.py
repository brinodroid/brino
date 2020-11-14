from django.apps import AppConfig


class BrcoreConfig(AppConfig):
    name = 'brCore'

    def ready(self):
        print('brcore ready called')


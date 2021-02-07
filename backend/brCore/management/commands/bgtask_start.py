from django.core.management.base import BaseCommand, CommandError
from common.actions.bgtask import start_bgtask
from brCore.models import BGTask

class Command(BaseCommand):
    help = 'Starts the bgtask'

    def handle(self, *args, **options):
        try:
            bgtaskList = BGTask.objects.all()
        except BGTask.DoesNotExist:
            raise CommandError('bgtask is empty')

        for bgtask in bgtaskList:
            self.stdout.write(self.style.SUCCESS('bgtask "%s"' % bgtask))
            start_bgtask(bgtask)

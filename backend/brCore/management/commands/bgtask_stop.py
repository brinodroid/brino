from django.core.management.base import BaseCommand, CommandError
from brCore.models import BGTask
from common.types.bgtask_types import BGTaskAction, BGTaskStatus

class Command(BaseCommand):
    help = 'Stop the bgtask'

    def handle(self, *args, **options):
        try:
            bgtaskList = BGTask.objects.all()
        except BGTask.DoesNotExist:
            raise CommandError('bgtask is empty')

        for bgtask in bgtaskList:
            self.stdout.write(self.style.SUCCESS('bgtask "%s"' % bgtask))
            bgtask.action = BGTaskAction.NONE.value
            bgtask.status = BGTaskStatus.IDLE.value
            bgtask.save()

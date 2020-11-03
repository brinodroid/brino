from django.core.management.base import BaseCommand, CommandError
from brCore.models import BGTask
from brCore.utils.bgtask_action import BGTaskAction
from brCore.utils.bgtask_status import BGTaskStatus

class Command(BaseCommand):
    help = 'Stop the bgtask'

    def handle(self, *args, **options):
        try:
            bgtaskList = BGTask.objects.all()
        except BGTask.DoesNotExist:
            raise CommandError('bgtask is empty')

        for bgtask in bgtaskList:
            self.stdout.write(self.style.SUCCESS('bgtask "%s"' % bgtask))
            bgtask.action = BGTaskAction.NO_ACTION.value
            bgtask.status = BGTaskStatus.NOT_STARTED.value
            bgtask.save()
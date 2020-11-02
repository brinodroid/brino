from django.db import models
from django.utils import timezone
from .utils.asset_types import AssetTypes
from .utils.bgtask_status import BGTaskStatus
from .utils.bgtask_action import BGTaskAction, BGTaskActionStatus


# WatchList: This is the list of assets actively tracked
class WatchList(models.Model):
    creationTimestamp = models.DateTimeField(editable=False, default=timezone.now)
    updateTimestamp = models.DateTimeField(default=timezone.now)
    assetType = models.CharField(max_length=16, choices=AssetTypes.choices(), default=AssetTypes.STOCK)
    ticker = models.CharField(max_length=20)
    # Going with float as sqlite doesnt have decimal support
    optionStrike = models.FloatField(null=True)
    optionExpiry = models.DateField(null=True)

    # Optional comments field
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.creationTimestamp = timezone.now()
        self.updateTimestamp = timezone.now()
        return super(WatchList, self).save(*args, **kwargs)

    def __str__(self):
        return "creationTimestamp: %s, updateTimestamp:%s, assetType:%s, ticker:%s," \
               " optionStrike:%s, optionExpiry:%s, comment:%s " \
              % (self.creationTimestamp, self.updateTimestamp, self.assetType, self.ticker,
                 self.optionStrike, self.optionExpiry, self.comment)

class BGTask(models.Model):
    updateTimestamp = models.DateTimeField(default=timezone.now)
    watchListId = models.IntegerField()
    status = models.CharField(max_length=16, choices=BGTaskStatus.choices(), default=BGTaskStatus.NOT_STARTED, null=True)
    action = models.CharField(max_length=64, choices=BGTaskAction.choices(), default=BGTaskAction.NO_ACTION)
    actionStatus = models.CharField(max_length=16, choices=BGTaskActionStatus.choices(), default=BGTaskActionStatus.NONE)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(BGTask, self).save(*args, **kwargs)

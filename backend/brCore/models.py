from django.db import models
from django.utils import timezone
from .utils.asset_types import AssetTypes
from .utils.bgtask_types import BGTaskAction, BGTaskActionResult, BGTaskStatus, BGTaskDataIdType


# WatchList: This is the list of assets actively tracked
class WatchList(models.Model):
    creationTimestamp = models.DateTimeField(editable=False, default=timezone.now)
    updateTimestamp = models.DateTimeField(default=timezone.now)
    assetType = models.CharField(max_length=16, choices=AssetTypes.choices(), default=AssetTypes.STOCK.value)
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
    dataId = models.IntegerField()
    dataIdType = models.CharField(max_length=16, choices=BGTaskDataIdType.choices(),
                                  default=BGTaskDataIdType.WATCHLIST.value)
    status = models.CharField(max_length=16, choices=BGTaskStatus.choices(),
                              default=BGTaskStatus.IDLE.value, null=True)
    action = models.CharField(max_length=64, choices=BGTaskAction.choices(),
                              default=BGTaskAction.NONE.value, null=True)
    actionResult = models.CharField(max_length=16, choices=BGTaskActionResult.choices(),
                                    default=BGTaskActionResult.NONE.value)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(BGTask, self).save(*args, **kwargs)


class PortFolio(models.Model):
    updateTimestamp = models.DateTimeField(default=timezone.now)
    watchListId = models.IntegerField()
    entryDate = models.DateField()
    entryPrice = models.FloatField()
    units = models.FloatField()
    exitPrice = models.FloatField(null=True, blank=True)
    exitDate = models.DateField(null=True, blank=True)
    profitTarget = models.FloatField()
    stopLoss = models.FloatField()
    chainedPortFolioId = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(PortFolio, self).save(*args, **kwargs)


from django.db import models
from django.utils import timezone
from .types.asset_types import AssetTypes, PortFolioSource, TransactionType
from .types.bgtask_types import BGTaskAction, BGTaskActionResult, BGTaskStatus, BGTaskDataIdType
from .types.scan_types import ScanStatus, ScanProfile
from .types.status_types import Status


# WatchList: This is the list of assets actively tracked
class WatchList(models.Model):
    creationTimestamp = models.DateTimeField(
        editable=False, default=timezone.now)
    updateTimestamp = models.DateTimeField(default=timezone.now)
    assetType = models.CharField(
        max_length=16, choices=AssetTypes.choices(), default=AssetTypes.STOCK.value)
    ticker = models.CharField(max_length=20)
    # Going with float as sqlite doesnt have decimal support
    optionStrike = models.FloatField(null=True)
    optionExpiry = models.DateField(null=True)
    brine_id = models.UUIDField(null=True)

    # Optional comments field
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.creationTimestamp = timezone.now()
        self.updateTimestamp = timezone.now()
        return super(WatchList, self).save(*args, **kwargs)

    def __str__(self):
        return "assetType:%s, ticker:%s, optionStrike:%s, optionExpiry:%s, comment:%s," \
               "brine_id:%s, creationTimestamp: %s, updateTimestamp:%s" \
               % (self.assetType, self.ticker, self.optionStrike, self.optionExpiry,
                  self.comment, self.brine_id, self.creationTimestamp, self.updateTimestamp)


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
    details = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(BGTask, self).save(*args, **kwargs)

    def __str__(self):
        return "dataIdType:%s, dataId:%s, status:%s, action:%s, details:%s" \
               " actionResult:%s, updateTimestamp:%s" \
               % (self.dataIdType, self.dataId, self.status, self.action, self.details,
                  self.actionResult, self.updateTimestamp)


class PortFolio(models.Model):
    updateTimestamp = models.DateTimeField(default=timezone.now)
    watchListId = models.IntegerField()
    entryDateTime = models.DateTimeField(null=False, blank=False, default=None)
    entryPrice = models.FloatField()
    units = models.FloatField()
    exitPrice = models.FloatField(null=True, blank=True)
    exitDateTime = models.DateTimeField(null=True, blank=True, default=None)

    profitTarget = models.FloatField()
    stopLoss = models.FloatField()
    ttype = models.CharField(max_length=16, choices=TransactionType.choices(),
                             default=TransactionType.BUY.value)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(PortFolio, self).save(*args, **kwargs)

    def __str__(self):
        return "watchListId:%s, entryDateTime:%s, entryPrice:%s, units:%s," \
               " profitTarget:%s, stopLoss:%s, brine_id:%s, source:%s, ttype:%s, \
                updateTimestamp:%s" \
               % (self.watchListId, self.entryDateTime, self.entryPrice, self.units,
                  self.profitTarget, self.stopLoss, self.brine_id, self.source,
                  self.ttype, self.updateTimestamp)


class ScanEntry(models.Model):
    updateTimestamp = models.DateTimeField(default=timezone.now)
    watchListId = models.IntegerField()
    profile = models.CharField(max_length=16, choices=ScanProfile.choices(),
                               default=ScanProfile.STOCK.value, null=True)
    support = models.FloatField()
    resistance = models.FloatField()
    profitTarget = models.FloatField(null=True, blank=True)
    stopLoss = models.FloatField(null=True, blank=True)
    etTargetPrice = models.FloatField(default=0)
    fvTargetPrice = models.FloatField(default=0)
    rationale = models.TextField(default="")

    # Filled by backend
    currentPrice = models.FloatField(null=True)
    volatility = models.TextField(null=True, blank=True)
    shortfloat = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=ScanStatus.choices(),
                              default=ScanStatus.NONE.value, null=True)
    details = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(ScanEntry, self).save(*args, **kwargs)

    def __str__(self):
        return "watchListId:%s, profile:%s, currentPrice:%s, support:%s, resistance:%s, profitTarget:%s, stopLoss:%s," \
            " etTargetPrice:%s, fvTargetPrice:%s, rationale:%s, volatility:%s, shortfloat:%s, status:%s," \
            "details:%s, updateTimestamp:%s" \
               % (self.watchListId, self.profile, self.currentPrice, self.support, self.resistance,
                  self.profitTarget, self.stopLoss, self.etTargetPrice, self.fvTargetPrice, self.rationale,
                  self.volatility, self.shortfloat, self.status, self.details, self.updateTimestamp)


class PortFolioUpdate(models.Model):
    updateTimestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value, null=True)

    status = models.CharField(max_length=16, choices=Status.choices(),
                              default=Status.NONE.value, null=True)

    def save(self, *args, **kwargs):
        self.updateTimestamp = timezone.now()
        return super(PortFolioUpdate, self).save(*args, **kwargs)

    def __str__(self):
        return "source:%s, status:%s, updateTimestamp:%s" \
               % (self.source, self.status, self.updateTimestamp)

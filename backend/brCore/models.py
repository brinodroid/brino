import logging
from django.db import models
from django.utils import timezone
from common.types.asset_types import AssetTypes, PortFolioSource, TransactionType
from common.types.bgtask_types import BGTaskAction, BGTaskActionResult, BGTaskStatus, BGTaskDataIdType
from common.types.scan_types import ScanStatus, ScanProfile
from common.types.status_types import Status

logger = logging.getLogger('django')



# WatchList: This is the list of assets actively tracked
class WatchList(models.Model):
    creation_timestamp = models.DateTimeField(
        editable=False, default=timezone.now)
    update_timestamp = models.DateTimeField(default=timezone.now)
    asset_type = models.CharField(
        max_length=16, choices=AssetTypes.choices(), default=AssetTypes.STOCK.value)
    ticker = models.CharField(max_length=20)
    # Going with float as sqlite doesnt have decimal support
    option_strike = models.FloatField(null=True)
    option_expiry = models.DateField(null=True)
    brine_id = models.UUIDField(null=True)

    # Optional comments field
    comment = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_timestamp = timezone.now()
        self.update_timestamp = timezone.now()
        return super(WatchList, self).save(*args, **kwargs)

    def __str__(self):
        return "asset_type:%s, ticker:%s, option_strike:%s, option_expiry:%s, comment:%s," \
               "brine_id:%s, creation_timestamp: %s, update_timestamp:%s" \
               % (self.asset_type, self.ticker, self.option_strike, self.option_expiry,
                  self.comment, self.brine_id, self.creation_timestamp, self.update_timestamp)


class BGTask(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)
    data_id = models.IntegerField()
    data_id_type = models.CharField(max_length=16, choices=BGTaskDataIdType.choices(),
                                  default=BGTaskDataIdType.WATCHLIST.value)
    status = models.CharField(max_length=16, choices=BGTaskStatus.choices(),
                              default=BGTaskStatus.IDLE.value, null=True)
    action = models.CharField(max_length=64, choices=BGTaskAction.choices(),
                              default=BGTaskAction.NONE.value, null=True)
    action_result = models.CharField(max_length=16, choices=BGTaskActionResult.choices(),
                                    default=BGTaskActionResult.NONE.value)
    details = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(BGTask, self).save(*args, **kwargs)

    def __str__(self):
        return "data_id_type:%s, data_id:%s, status:%s, action:%s, details:%s" \
               " action_result:%s, update_timestamp:%s" \
               % (self.data_id_type, self.data_id, self.status, self.action, self.details,
                  self.action_result, self.update_timestamp)


class PortFolio(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)
    watchlist_id = models.IntegerField()
    entry_datetime = models.DateTimeField(null=False, blank=False, default=None)
    entry_price = models.FloatField()
    units = models.FloatField()
    exit_price = models.FloatField(null=True, blank=True)
    exit_datetime = models.DateTimeField(null=True, blank=True, default=None)

    transaction_type = models.CharField(max_length=16, choices=TransactionType.choices(),
                             default=TransactionType.BUY.value)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(PortFolio, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id:%s, entry_datetime:%s, entry_price:%s, units:%s," \
               " brine_id:%s, source:%s, transaction_type:%s, \
                update_timestamp:%s" \
               % (self.watchlist_id, self.entry_datetime, self.entry_price, self.units,
                  self.brine_id, self.source,
                  self.transaction_type, self.update_timestamp)


class ScanEntry(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)
    watchlist_id = models.IntegerField()
    portfolio_id = models.IntegerField(default=0)
    profile = models.CharField(max_length=16, choices=ScanProfile.choices(),
                               default=ScanProfile.BUY_STOCK.value, null=True)
    profit_target = models.FloatField(null=True, blank=True)
    stop_loss = models.FloatField(null=True, blank=True)
    support = models.FloatField(null=True, blank=True)
    resistance = models.FloatField(null=True, blank=True)
    brate_target = models.FloatField(null=True, blank=True)
    brifz_target = models.FloatField(null=True, blank=True)
    rationale = models.TextField(default="", blank=True)
    reward_2_risk = models.FloatField(null=True, blank=True)
    potential = models.FloatField(null=True, blank=True)
    active_track = models.BooleanField(default=False)
    order_id = models.IntegerField(null=True, blank=True)

    # Filled by backend
    current_price = models.FloatField(null=True)
    volatility = models.TextField(null=True, blank=True)
    short_float = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=ScanStatus.choices(),
                              default=ScanStatus.NONE.value, null=True)
    details = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(ScanEntry, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id:%s, portfolio_id:%s, profile:%s, current_price:%s, support:%s, resistance:%s," \
            " profit_target:%s, stop_loss:%s, brate_target:%s, brifz_target:%s, rationale:%s, reward_2_risk:%s," \
            " potential:%s, active_track:%s, order_id:%s" \
            " volatility:%s, short_float:%s, status:%s, details:%s, update_timestamp:%s" \
               % (self.watchlist_id, self.portfolio_id, self.profile, self.current_price, self.support, self.resistance,
                  self.profit_target, self.stop_loss, self.brate_target, self.brifz_target, self.rationale, self.reward_2_risk,
                  self.potential, self.active_track, self.order_id,
                  self.volatility, self.short_float, self.status, self.details, self.update_timestamp)


class PortFolioUpdate(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value, null=True)

    status = models.CharField(max_length=16, choices=Status.choices(),
                              default=Status.NONE.value, null=True)
    details = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(PortFolioUpdate, self).save(*args, **kwargs)

    def __str__(self):
        return "source:%s, status:%s, details=%s, update_timestamp:%s" \
               % (self.source, self.status, self.details, self.update_timestamp)

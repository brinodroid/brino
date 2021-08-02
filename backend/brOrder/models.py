from django.db import models
from django.utils import timezone
from common.types.asset_types import PortFolioSource, TransactionType
from brOrder.order_types import OrderAction

# Model presenting a open order
class OpenOrder(models.Model):
    created_datetime = models.DateTimeField(editable=False, default=timezone.now)
    update_timestamp = models.DateTimeField(default=timezone.now)

    watchlist_id_list = models.TextField(default=None)
    transaction_type_list = models.TextField(default=None)
    strategy_id = models.IntegerField(blank=True, null=True)

    price = models.FloatField()
    units = models.FloatField()
    action = models.CharField(max_length=16, choices=OrderAction.choices(), default=OrderAction.OPEN.value)

    opening_strategy = models.TextField(null=True, blank=True, default=None)
    closing_strategy = models.TextField(null=True, blank=True, default=None)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)
    submit = models.BooleanField(default=False)
    #We need to refer to historical data too

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_datetime = timezone.now()
        self.update_timestamp = timezone.now()
        return super(OpenOrder, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id_list:%s, transaction_type_list:%s, strategy_id:%s, " \
               " price:%s, units:%s, action:%s, brine_id:%s, source:%s, submit:%s,"\
               " opening_strategy:%s, closing_strategy:%s, created_datetime:%s, update_timestamp:%s" \
               % (self.watchlist_id_list, self.transaction_type_list, self.strategy_id,
                  self.price, self.units, self.action, self.brine_id, self.source, self.submit,
                  self.opening_strategy, self.closing_strategy, self.created_datetime, self.update_timestamp)

# Model presenting a executed order
class ExecutedOrder(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)

    watchlist_id_list = models.TextField(default=None)
    transaction_type_list = models.TextField(default=None)

    order_created_datetime = models.DateTimeField(null=False, blank=False, default=None)
    price = models.FloatField()
    units = models.FloatField()

    executed_datetime = models.DateTimeField(null=False, blank=False, default=None)
    executed_price = models.FloatField()

    opening_strategy = models.TextField(null=True, blank=True, default=None)
    closing_strategy = models.TextField(null=True, blank=True, default=None)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(ExecutedOrder, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id_list:%s, transaction_type_list:%s, order_created_datetime:%s,"\
               " price:%s, units:%s, brine_id:%s, source:%s, executed_datetime:%s, executed_price:%s," \
               " opening_strategy:%s, closing_strategy:%s, update_timestamp:%s" \
               % (self.watchlist_id_list, self.transaction_type_list, self.order_created_datetime,
                  self.price, self.units, self.brine_id, self.source, self.executed_datetime,
                  self.executed_price, self.opening_strategy, self.closing_strategy, self.update_timestamp)

# Model presenting a cancelled order
class CancelledOrder(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)

    watchlist_id_list = models.TextField(default=None)
    transaction_type_list = models.TextField(default=None)

    created_datetime = models.DateTimeField(null=False, blank=False, default=None)
    price = models.FloatField()
    units = models.FloatField()

    cancelled_datetime = models.DateTimeField(null=False, blank=False, default=None)

    opening_strategy = models.TextField(null=True, blank=True, default=None)
    closing_strategy = models.TextField(null=True, blank=True, default=None)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(CancelledOrder, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id_list:%s, transaction_type_list:%s, created_datetime:%s,"\
               " price:%s, units:%s, brine_id:%s, source:%s, opening_strategy:%s,"\
               " closing_strategy:%s, update_timestamp:%s, cancelled_datetime:%s" \
               % (self.watchlist_id_list, self.transaction_type_list, self.created_datetime,
                  self.price, self.units, self.brine_id, self.source, self.opening_strategy,
                  self.closing_strategy, self.update_timestamp, self.cancelled_datetime)

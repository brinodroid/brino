from django.db import models
from django.utils import timezone
from common.types.asset_types import PortFolioSource, TransactionType

# Model presenting a pending order
class Order(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)

    watchlist_id_list = models.TextField(default=None)
    transaction_type_list = models.TextField(default=None)

    entry_datetime = models.DateTimeField(null=False, blank=False, default=None)
    entry_price = models.FloatField()
    units = models.FloatField()

    opening_strategy = models.TextField(null=True, blank=True, default=None)
    closing_strategy = models.TextField(null=True, blank=True, default=None)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id_list:%s, transaction_type_list:%s, entry_datetime:%s,"\
               " entry_price:%s, units:%s, brine_id:%s, source:%s, opening_strategy:%s,"\
               " closing_strategy:%s, update_timestamp:%s" \
               % (self.watchlist_id_list, self.transaction_type_list, self.entry_datetime,
                  self.entry_price, self.units, self.brine_id, self.source, self.opening_strategy,
                  self.closing_strategy, self.update_timestamp)

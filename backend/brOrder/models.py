from django.db import models
from django.utils import timezone
from brCore.types.asset_types import PortFolioSource, TransactionType

# Model presenting a pending order
class Order(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)

    watchlist_id = models.IntegerField()
    entry_datetime = models.DateTimeField(null=False, blank=False, default=None)
    entry_price = models.FloatField()
    units = models.FloatField()

    transaction_type = models.CharField(max_length=16, choices=TransactionType.choices(),
                             default=TransactionType.BUY.value)
    brine_id = models.UUIDField(null=True)
    source = models.CharField(max_length=16, choices=PortFolioSource.choices(),
                              default=PortFolioSource.BRINE.value)

    def save(self, *args, **kwargs):
        self.update_timestamp = timezone.now()
        return super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return "watchlist_id:%s, entry_datetime:%s, entry_price:%s, units:%s," \
               " brine_id:%s, source:%s, transaction_type:%s, \
                update_timestamp:%s" \
               % (self.watchlist_id, self.entry_datetime, self.entry_price, self.units,
                  self.brine_id, self.source,
                  self.transaction_type, self.update_timestamp)

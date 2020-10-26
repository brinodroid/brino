from django.db import models
from django.utils import timezone
from .utils.asset_types import AssetTypes

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

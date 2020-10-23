from django.db import models
from django.utils import timezone
from .utils import AssetTypes
from .utils import TransactionTypes
from .utils import ActionTypes


# PortFolio
class PortFolio(models.Model):
    creationTimestamp = models.DateTimeField(editable=False, default=timezone.now)
    updateTimestamp = models.DateTimeField(default=timezone.now)
    assetType = models.IntegerField(choices=AssetTypes.choices(), default=AssetTypes.STOCK)
    transactionType = models.IntegerField(choices=TransactionTypes.choices(), default=TransactionTypes.BUY)
    ticker = models.CharField(max_length=20)
    # Going with float as sqlite doesnt have decimal support
    optionStrike = models.FloatField()
    optionExpiry = models.DateField()
    costPrice = models.FloatField()
    units = models.FloatField()
    profitTarget = models.FloatField()
    stopLoss = models.FloatField()

    ratingChSRating = models.CharField(max_length=2)
    ratingETRating = models.IntegerField()
    ratingETTargetPrice = models.FloatField()
    ratingFidRating = models.FloatField()
    ratingRHRating = models.IntegerField()
    ratingFVRating = models.FloatField()
    ratingFVTargetPrice = models.FloatField()
    comment = models.TextField()

    #Any actions on the port folio
    actionType = models.IntegerField(choices=ActionTypes.choices(), default=ActionTypes.ACTION_NOTHING)

    def save(self, *args, **kwargs):
        if not self.id:
            self.creationTimestamp = timezone.now()
        self.updateTimestamp = timezone.now()
        return super(PortFolio, self).save(*args, **kwargs)

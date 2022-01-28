from django.db import models
from django.utils import timezone
from brGaze.nnmodel_types import NNModelTypes

# Training: This is the list of assets actively tracked
class NNModelStatus(models.Model):
    update_timestamp = models.DateTimeField(default=timezone.now)

    watchlist_id = models.IntegerField()

    nnmodel_type = models.CharField(
        max_length=16, choices=NNModelTypes.choices(), default=NNModelTypes.LSTM.value)
    trained_till_date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_timestamp = timezone.now()
        self.update_timestamp = timezone.now()
        return super(NNModelStatus, self).save(*args, **kwargs)

    def __str__(self):
        return "update_timestamp:%s, watchlist_id:%s," \
               " nnmodel_type:%s, trained_till_date: %s" \
               % (self.update_timestamp, self.watchlist_id,
                    self.nnmodel_type, self.trained_till_date)

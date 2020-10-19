from django.db import models
from django.utils import timezone

# Global configurations settings for the app.
class Configuration(models.Model):
    creationTimestamp = models.DateTimeField(editable=False, default=timezone.now)
    updateTimestamp = models.DateTimeField(default=timezone.now)
    profitTargetPercent = models.IntegerField()
    stopLossPercent = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.creationTimestamp = timezone.now()
        self.updateTimestamp = timezone.now()
        return super(Configuration, self).save(*args, **kwargs)

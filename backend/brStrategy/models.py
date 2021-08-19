import logging
from django.db import models
from django.utils import timezone
from brStrategy.strategy_types import StrategyType
from brCore.models import PortFolio

logger = logging.getLogger('django')


# Strategy
class Strategy(models.Model):
    strategy_type = models.CharField(max_length=32, choices=StrategyType.choices())
    stop_loss = models.FloatField(blank=True, null=True)
    profit_target = models.FloatField(blank=True, null=True)
    active_track = models.BooleanField(default=False)

    #Create portfolio_id as a nullable foriegn key
    portfolio_id = models.ForeignKey(PortFolio, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    creation_timestamp = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_timestamp = timezone.now()
        return super(Strategy, self).save(*args, **kwargs)

    def __str__(self):
        return "strategy_type:%s, portfolio_id:%s, stop_loss:%s, profit_target:%s, active_track:%s" \
               % (self.strategy_type, self.portfolio_id, self.stop_loss, self.profit_target, self.active_track)

import logging
import sys
from django.db import models
from django.utils import timezone
from brStrategy.strategy_types import StrategyType
from brCore.models import PortFolio

logger = logging.getLogger('django')


# Strategy
class Strategy(models.Model):
    strategy_type = models.CharField(max_length=32, choices=StrategyType.choices())
    #Create portfolio_id as a nullable foriegn key
    portfolio_id = models.IntegerField(default=None, blank=True, null=True)
    watchlist_id = models.IntegerField(default=None, blank=True, null=True)

    stop_loss = models.FloatField(blank=True, null=True)
    profit_target = models.FloatField(blank=True, null=True)

    highest_price = models.FloatField(default=sys.float_info.min, null=True)
    lowest_price = models.FloatField(default=sys.float_info.max, null=True)

    active_track = models.BooleanField(default=False)

    creation_timestamp = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_timestamp = timezone.now()
        return super(Strategy, self).save(*args, **kwargs)

    def __str__(self):
        return "strategy_type:%s, portfolio_id:%s, watchlist_id:%s, stop_loss:%s, profit_target:%s,"\
            " highest_price:%s, lowest_price:%s, active_track:%s" \
            % (self.strategy_type, self.portfolio_id, self.watchlist_id, self.stop_loss, self.profit_target,
                self.highest_price, self.lowest_price, self.active_track)

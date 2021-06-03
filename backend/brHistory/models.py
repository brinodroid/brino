import logging
from django.db import models
from django.utils import timezone


# CallOptionData: This is the list of assets actively tracked
class CallOptionData(models.Model):
    date = models.DateField(null=True)
    watchlist_id = models.IntegerField()

    mark_price = models.FloatField()
    ask_price = models.FloatField()
    bid_price = models.FloatField()

    high_price = models.FloatField()
    low_price = models.FloatField()
    last_trade_price = models.FloatField()

    open_interest = models.IntegerField()
    volume = models.IntegerField()
    ask_size = models.IntegerField()
    bid_size = models.IntegerField()

    # Greeks
    delta = models.FloatField()
    gamma = models.FloatField()
    implied_volatility = models.FloatField()
    rho = models.FloatField()
    theta = models.FloatField()
    vega = models.FloatField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now().date()
        return super(CallOptionData, self).save(*args, **kwargs)

    def __str__(self):
        return "date:%s, watchlist_id:%s," \
               " mark_price:%s, ask_price: %s, bid_price:%s," \
               " high_price:%s, low_price: %s, last_trade_price:%s," \
               " open_interest:%s, volume: %s, ask_size:%s, bid_size:%s," \
               " delta:%s, gamma: %s, implied_volatility:%s, rho:%s, theta:%s, vega:%s" \
               % (self.date, self.watchlist_id,
                  self.mark_price, self.ask_price, self.bid_price,
                  self.high_price, self.low_price, self.last_trade_price,
                  self.open_interest, self.volume, self.ask_size, self.bid_size,
                  self.delta, self.gamma, self.implied_volatility, self.rho, self.theta, self.vega)

# PutOptionData: This is the list of assets actively tracked
class PutOptionData(models.Model):
    date = models.DateField(null=True)
    watchlist_id = models.IntegerField()

    mark_price = models.FloatField()
    ask_price = models.FloatField()
    bid_price = models.FloatField()

    high_price = models.FloatField()
    low_price = models.FloatField()
    last_trade_price = models.FloatField()

    open_interest = models.IntegerField()
    volume = models.IntegerField()
    ask_size = models.IntegerField()
    bid_size = models.IntegerField()

    # Greeks
    delta = models.FloatField()
    gamma = models.FloatField()
    implied_volatility = models.FloatField()
    rho = models.FloatField()
    theta = models.FloatField()
    vega = models.FloatField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now().date()
        return super(PutOptionData, self).save(*args, **kwargs)

    def __str__(self):
        return "date:%s, watchlist_id:%s," \
               " mark_price:%s, ask_price: %s, bid_price:%s," \
               " high_price:%s, low_price: %s, last_trade_price:%s," \
               " open_interest:%s, volume: %s, ask_size:%s, bid_size:%s," \
               " delta:%s, gamma: %s, implied_volatility:%s, rho:%s, theta:%s, vega:%s" \
               % (self.date, self.watchlist_id,
                  self.mark_price, self.ask_price, self.bid_price,
                  self.high_price, self.low_price, self.last_trade_price,
                  self.open_interest, self.volume, self.ask_size, self.bid_size,
                  self.delta, self.gamma, self.implied_volatility, self.rho, self.theta, self.vega)
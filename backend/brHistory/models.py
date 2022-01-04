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

# StockData: This is the list of assets actively tracked
class StockData(models.Model):
    date = models.DateField()
    watchlist_id = models.IntegerField()

    high_price = models.FloatField()
    low_price = models.FloatField()
    open_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.FloatField()

    average_volume_2_weeks = models.FloatField(null=True)
    average_volume = models.FloatField(null=True)
    dividend_yield = models.FloatField(null=True)
    market_cap = models.FloatField(null=True)
    pb_ratio = models.FloatField(null=True)
    pe_ratio = models.FloatField(null=True)

    # These are low frequency changes. Keeping it in history for consistency
    low_52_weeks = models.FloatField(null=True)
    high_52_weeks = models.FloatField(null=True)
    num_employees = models.FloatField(null=True)
    shares_outstanding = models.FloatField(null=True)
    float = models.FloatField(null=True)


    def save(self, *args, **kwargs):
        return super(StockData, self).save(*args, **kwargs)

    def __str__(self):
        return "date:%s, watchlist_id:%s," \
               " high_price:%s, low_price: %s, open_price:%s, close_price:%s, volume: %s,"\
               " average_volume_2_weeks:%s, average_volume:%s, dividend_yield:%s, market_cap:%s," \
               " pb_ratio:%s, pe_ratio:%s, low_52_weeks:%s, high_52_weeks:%s," \
               " num_employees:%s, shares_outstanding:%s, float:%s" \
               % (self.date, self.watchlist_id,
                    self.high_price, self.low_price, self.open_price, self.open_price, self.volume,
                    self.average_volume_2_weeks, self.average_volume, self.dividend_yield, self.market_cap,
                    self.pb_ratio, self.pe_ratio, self.low_52_weeks, self.high_52_weeks,
                    self.num_employees, self.shares_outstanding, self.float)

from rest_framework import serializers
from brHistory.models import CallOptionData, PutOptionData, StockData

class CallOptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallOptionData
        fields = ('id', 'date', 'watchlist_id',
                  'mark_price', 'ask_price', 'bid_price',
                  'high_price', 'low_price', 'last_trade_price',
                  'open_interest', 'volume', 'ask_size', 'bid_size',
                  'delta', 'gamma', 'implied_volatility', 'rho', 'theta', 'vega')


class PutOptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PutOptionData
        fields = ('id', 'date', 'watchlist_id',
                  'mark_price', 'ask_price', 'bid_price',
                  'high_price', 'low_price', 'last_trade_price',
                  'open_interest', 'volume', 'ask_size', 'bid_size',
                  'delta', 'gamma', 'implied_volatility', 'rho', 'theta', 'vega')

class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ('id', 'date', 'watchlist_id',
                  'high_price', 'low_price', 'open_price', 'close_price', 'volume',
                  'average_volume_2_weeks', 'average_volume', 'dividend_yield', 'market_cap',
                  'pb_ratio', 'pe_ratio', 'low_52_weeks', 'high_52_weeks',
                  'num_employees', 'shares_outstanding', 'float'
                  )
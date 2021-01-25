from rest_framework import serializers
from .models import CallOptionData, PutOptionData

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
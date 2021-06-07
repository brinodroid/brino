from rest_framework import serializers
from ..models import ScanEntry


class ScanEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanEntry
        fields = ('id', 'update_timestamp', 'watchlist_id', 'portfolio_id', 'profile', 'current_price', 'support', 'resistance', 'profit_target',
                  'stop_loss', 'brate_target', 'brifz_target', 'rationale', 'reward_2_risk', 'potential', 'active_track', 'order_id',
                  'volatility', 'short_float', 'status', 'details')

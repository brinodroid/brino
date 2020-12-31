from rest_framework import serializers
from ..models import ScanEntry


class ScanEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanEntry
        fields = ('id', 'updateTimestamp', 'watchListId', 'currentPrice', 'support', 'resistance',
                  'profitTarget', 'stopLoss', 'rationale', 'volatility', 'status', 'details')
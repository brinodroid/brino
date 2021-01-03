from rest_framework import serializers
from ..models import ScanEntry


class ScanEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanEntry
        fields = ('id', 'updateTimestamp', 'watchListId', 'linkedScanId', 'currentPrice', 'support', 'resistance', 'profitTarget',
                  'stopLoss', 'etTargetPrice', 'fvTargetPrice', 'rationale', 'volatility', 'shortfloat', 'status', 'details')

from rest_framework import serializers
from brStrategy.models import Strategy

class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ('id', 'strategy_type', 'stop_loss', 'profit_target', 'portfolio_id',
            'active_track', 'creation_timestamp')
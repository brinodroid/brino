from rest_framework import serializers
from ..models import WatchList


class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = ('id', 'creation_timestamp', 'update_timestamp',
                  'asset_type', 'ticker', 'option_strike', 'option_expiry',
                  'brine_id', 'comment')

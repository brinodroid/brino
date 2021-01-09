from rest_framework import serializers
from ..models import WatchList


class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = ('id', 'creationTimestamp', 'updateTimestamp',
                  'assetType', 'ticker', 'optionStrike', 'optionExpiry',
                  'brine_id', 'comment')

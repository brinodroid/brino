from rest_framework import serializers
from ..models import PortFolio, PortFolioUpdate


class PortFolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortFolio
        fields = ('id', 'update_timestamp', 'watchlist_id', 'entry_datetime',
                  'entry_price', 'units', 'exit_price', 'exit_datetime', 'transaction_type',
                  'brine_id', 'source')


class PortFolioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortFolioUpdate
        fields = ('id', 'update_timestamp', 'source', 'status', 'details')

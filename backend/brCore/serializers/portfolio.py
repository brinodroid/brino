from rest_framework import serializers
from ..models import PortFolio, PortFolioUpdate


class PortFolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortFolio
        fields = ('id', 'updateTimestamp', 'watchListId', 'entryDateTime',
                  'entryPrice', 'units', 'exitPrice', 'exitDateTime', 'ttype',
                  'profitTarget', 'stopLoss', 'brine_id', 'source')


class PortFolioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortFolioUpdate
        fields = ('id', 'updateTimestamp', 'source', 'status')

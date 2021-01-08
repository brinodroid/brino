from rest_framework import serializers
from ..models import PortFolio, PortFolioUpdate


class PortFolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortFolio
        fields = ('id', 'updateTimestamp', 'watchListId', 'entryDate', 'entryPrice', 'units',
                  'exitPrice', 'exitDate', 'profitTarget', 'stopLoss', 'chainedPortFolioId')


class PortFolioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortFolioUpdate
        fields = ('id', 'updateTimestamp', 'source', 'status')

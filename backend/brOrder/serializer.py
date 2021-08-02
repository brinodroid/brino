from rest_framework import serializers
from .models import OpenOrder, ExecutedOrder, CancelledOrder

class OpenOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenOrder
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list',
         'created_datetime', 'price', 'units', 'action', 'opening_strategy', 'closing_strategy',
         'brine_id', 'source', 'submit', 'strategy_id')

class ExecutedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutedOrder
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list',
         'order_created_datetime', 'price', 'units', 'executed_datetime','executed_price',
         'opening_strategy', 'closing_strategy', 'brine_id', 'source', 'submit')

class CancelledOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelledOrder
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list',
         'created_datetime', 'price', 'units', 'opening_strategy', 'closing_strategy',
         'cancelled_datetime', 'brine_id', 'source', 'submit')
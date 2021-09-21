from rest_framework import serializers
from .models import OpenOrder, ExecutedOrder, CancelledOrder
import brCore.watchlist_bll as watchlist_bll


class OpenOrderSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()

    def get_current_price(self, open_order_instance):
        watchlist = watchlist_bll.get_watchlist(open_order_instance.watchlist_id_list)
        return watchlist_bll.get_watchlist_latest_price(watchlist, True)

    class Meta:
        model = OpenOrder
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list',
         'created_datetime', 'price', 'units', 'action', 'opening_strategy', 'closing_strategy',
         'brine_id', 'source', 'submit', 'strategy_id', 'current_price')

class ExecutedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutedOrder
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list',
         'order_created_datetime', 'price', 'units', 'executed_datetime','executed_price',
         'opening_strategy', 'closing_strategy', 'brine_id', 'source')

class CancelledOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelledOrder
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list',
         'created_datetime', 'price', 'units', 'opening_strategy', 'closing_strategy',
         'cancelled_datetime', 'brine_id', 'source')
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'update_timestamp', 'watchlist_id_list', 'transaction_type_list', 'entry_datetime',
         'entry_price', 'units', 'opening_strategy', 'closing_strategy', 'brine_id', 'source')

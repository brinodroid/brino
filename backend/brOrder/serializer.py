from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'update_timestamp', 'watchlist_id', 'entry_datetime',
                  'entry_price', 'units', 'transaction_type', 'brine_id', 'source')

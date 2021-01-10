from rest_framework import serializers
from ..models import BGTask


class BGTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BGTask
        fields = ('id', 'update_timestamp', 'data_id_type', 'data_id', 'status', 'action', 'action_result', 'details')

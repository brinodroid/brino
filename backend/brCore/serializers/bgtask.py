from rest_framework import serializers
from ..models import BGTask


class BGTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BGTask
        fields = ('id', 'updateTimestamp', 'dataIdType', 'dataId', 'status', 'action', 'actionResult')

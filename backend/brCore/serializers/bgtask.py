from rest_framework import serializers
from ..models import BGTask


class BGTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BGTask
        fields = ('id', 'updateTimestamp', 'dataId', 'status', 'action')

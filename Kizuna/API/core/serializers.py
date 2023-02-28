from rest_framework import serializers
from API.models import WebroomTransaction


class WebroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebroomTransaction
        fields = ("event", "roomid", "webinarId")





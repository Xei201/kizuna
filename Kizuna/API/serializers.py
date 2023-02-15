from rest_framework import serializers
from .models import WebroomTransaction


class WebroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebroomTransaction
        fields = ("event", "roomid", "webinarId")





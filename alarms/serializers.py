from rest_framework import serializers
from .models import Alarm
from goals.serializers import GoalListSerializer

# 알람 생성
class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        exclude = ('alarm_from',)
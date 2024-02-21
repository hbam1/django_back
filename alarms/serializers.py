from rest_framework import serializers
from .models import Alarm
from goals.models import Goal
from goals.serializers import TagSerializer, ActivityTagSerializer
from rooms.models import Room


# 알람 생성
class AlarmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alarm
        exclude = ('alarm_from',)


# 알람 목표
class AlarmGoalSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    activity_tags = ActivityTagSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        exclude = ("content", "is_in_group", "is_completed", "belonging_group_id",)


# 알람 방
class AlarmRoomSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    activity_tags = ActivityTagSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        exclude = ("detail", "members", "cert_detail", "is_active", "duration", "closing_date", "penalty_bank",)


# 알람 조회
class AlarmListSerializer(serializers.ModelSerializer):
    goals = AlarmGoalSerializer(read_only=True)
    rooms = AlarmRoomSerializer(read_only=True)

    class Meta:
        model = Alarm
        fields = "__all__"
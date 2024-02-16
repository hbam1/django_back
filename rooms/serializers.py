from rest_framework import serializers
from goals.serializers import TagSerializer, ActivityTagSerializer
from .models import *

# 방 생성
class RoomSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    activity_tags = ActivityTagSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        exclude = ["members", "master", "is_active"]
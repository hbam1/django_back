from rest_framework import serializers
from goals.serializers import TagSerializer, ActivityTagSerializer
from .models import *

# 임시로 사용하는 방 기본 시리얼라이저(전체 포함)
# 현재 사용 범위 : 추천 get view(관리를 위해 사용시 추가바람)
class RoomDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

# 방 생성
class RoomSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    activity_tags = ActivityTagSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        exclude = ["members", "master", "is_active", "closing_date", "penalty_bank",]
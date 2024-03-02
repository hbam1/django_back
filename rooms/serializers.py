from rest_framework import serializers
from goals.models import Goal
from .models import *

# 임시로 사용하는 방 기본 시리얼라이저(전체 포함)
# 현재 사용 범위 : 추천 get view(관리를 위해 사용시 추가바람)
class RoomDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


# 방 생성 시 목표 조회
class GoalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = (
            "id",
            "title",
        )


# 방 생성
class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "title",
            "detail",
            "duration",
            "favor_offline",
            "cert_required",
            "cert_detail",
            "penalty_value",
            "deposit",
        )
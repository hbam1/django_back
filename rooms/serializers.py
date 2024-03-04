from rest_framework import serializers
from goals.models import Goal
from goals.serializers import ActivityTagSerializer, TagSerializer
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


# master serializer
class RoomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "nickname",
        )


# 방 리스트 조회
class RoomListSerializer(serializers.ModelSerializer):
        master = RoomUserSerializer(read_only=True)
        tags = TagSerializer(many=True, read_only=True)
        activity_tags = ActivityTagSerializer(many=True, read_only=True)
        current_user_id = serializers.SerializerMethodField()  # 새로운 필드 추가

        class Meta:
            model = Room
            fields = (
                "id",
                "title",
                "members",
                "master",
                "tags",
                "activity_tags",
                "is_active",
                "closing_date",
                "current_user_id",  # 새로운 필드 추가
            )
        # 프론트에서 로그인한 유저가 방장인지 아닌지 판단하기 위해 필요
        def get_current_user_id(self, obj):
            # 현재 요청한 사용자의 ID를 반환합니다.
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                return request.user.id
            return None

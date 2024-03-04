from rest_framework import serializers
from goals.models import Goal, Tag, ActivityTag, AchievementReport, User

# 목표 태그 조회
class TagSerializer(serializers.ModelSerializer):
    parent_tag = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ("id", "tag_name", "parent_tag")

    # 부모 태그 이름으로 클라이언트에게 반환
    def get_parent_tag(self, obj):
        if obj.parent_tag:
            return obj.parent_tag.tag_name
        return None

# 활동 태그 조회
class ActivityTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTag
        fields = ("id", "tag_name",)

# 임시로 사용하는 기본 목표 시리얼라이저(전체 포함)
# 현재 사용 범위 : 추천 get view(관리를 위해 사용시 추가바람)
class GoalDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

# 목표 생성 serializer
class GoalSerializer(serializers.ModelSerializer):
    # tag들은 임의로 만들어서 넣지 못하게 views에서 처리
    tags = TagSerializer(many=True, read_only=True)
    activity_tags = ActivityTagSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "is_in_group",
            "is_completed",
            "belonging_group_id",
            "user",
        )
        

class UserForARSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname']  # User 모델의 id와 nickname 필드를 전송

class GoalForARSerializer(serializers.ModelSerializer):
    user = UserForARSerializer()  

    class Meta:
        model = Goal
        fields = ['id', 'title', 'user']  # Goal 모델의 id, title, user 필드를 전송

class AchievementReportSerializer(serializers.ModelSerializer):
    goal = GoalForARSerializer(read_only=True)  # GoalForARSerializer를 사용하여 goal 필드를 직렬화

    class Meta:
        model = AchievementReport
        fields = '__all__'
        read_only_fields = ('reacted_love', 'reacted_respectful', 'reacted_dislike')


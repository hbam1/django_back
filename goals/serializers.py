from rest_framework import serializers
from goals.models import Goal, Tag, ActivityTag

# 목표 태그 조회
class TagSerializer(serializers.ModelSerializer):
    parent_tag = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ("tag_name", "parent_tag")

    # 부모 태그 이름으로 클라이언트에게 반환
    def get_parent_tag(self, obj):
        if obj.parent_tag:
            return obj.parent_tag.tag_name
        return None

# 활동 태그 조회
class ActivityTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTag
        fields = ("tag_name",)

# 목표 생성 serializer
class GoalSerializer(serializers.ModelSerializer):
    # tag들은 임의로 만들어서 넣지 못하게 views에서 처리
    tags = TagSerializer(many=True, read_only=True)
    activity_tags = ActivityTagSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        exclude = ("is_in_group", "is_completed", "belonging_group_id", "user",) # user는 views에서 저장


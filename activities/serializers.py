from rest_framework import serializers
from .models import *


# 회원 활동 정보
class UserActivityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityInfo
        fields = '__all__'

# 방장이 만드는 인증
class AuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authentication
        fields = '__all__'

# 멤버가 하는 인증
class MemberAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberAuthentication
        exclude = ("user",)


#로그 출력 용
class AuthLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberAuthentication
        exclude = ("content", "image",)

    def get_user(self, obj):
        user_info = {
            'id': obj.user.id,
            'nickname': obj.user.nickname
        }
        return user_info
    
# 개설된 전체 인증 조회용
class AuthListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authentication
        fields = "__all__"

# 자유게시판 게시글
class FreeBoardPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = (
            "author",
            "room",
            "created_at",
            "updated_at",
            "voter",
        )

# 자유게시판 게시글 댓글
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = (
            "author",
            "post",
            "created_at",
            "updated_at",
            "voter",
        )

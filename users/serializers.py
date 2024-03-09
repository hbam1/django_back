from .models import User
from rest_framework import serializers


# 회원가입
class UserSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nickname = serializers.CharField(required=False)
    password = serializers.CharField()
    password2 = serializers.CharField()

    # 이메일
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            return serializers.ValidationError("이미 존재하는 이메일입니다.")
        return value

    # 패스워드 확인
    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")
        if password != password2:
            raise serializers.ValidationError("두 비밀번호가 일치하지 않습니다.")
        return data


# 회원정보조회
class UserInfoSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    fuel = serializers.IntegerField()
    completed_goals = serializers.IntegerField()
    all_goals = serializers.IntegerField()

class UserSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "nickname")

#마이페이지용 회원정보조회
class UserInfSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

#멤버 리스트 조회용
class MemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        depth = 1

# 회원가입 후 유저세부정보 입력
class UserSignupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "nickname",
            "profile",
            "region",
            "region_detail",
        )

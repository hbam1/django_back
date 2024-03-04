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
    nickname = serializers.CharField(source='user.nickname')
    fuel = serializers.IntegerField(source='user.fuel')
    completed_goals = serializers.IntegerField()
    all_goals = serializers.IntegerField()

#마이페이지용 회원정보조회
class UserInfSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
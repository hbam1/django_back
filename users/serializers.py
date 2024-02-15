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
class UserSerializer(serializers.ModelSerializer):
    # 회원정보 수정 시 값을 변경할 수 없음.
    # 나중에 비밀번호를 수정하는 serialzier는 따로 생성.
    email = serializers.EmailField(read_only=True)
    fuel = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
        exclude = ("password", "is_superuser", "is_active", "is_staff",)
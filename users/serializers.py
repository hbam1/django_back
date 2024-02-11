from .models import User
from rest_framework import serializers


class UserSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    # 이메일
    def validate_username(self, value):
        if User.objects.filter(email=value).exists():
            return serializers.ValidationError("이미 존재하는 이메일입니다.")
        return value

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")
        if password != password2:
            raise serializers.ValidationError("두 비밀번호가 일치하지 않습니다.")
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", )
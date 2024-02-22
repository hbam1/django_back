from rest_framework import serializers
from .models import UserActivityInfo


# 회원 활동 정보
class UserActivityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityInfo
        fields = '__all__'
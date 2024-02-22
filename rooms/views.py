from django.shortcuts import render
from rest_framework import viewsets, status
from goals.models import Tag, ActivityTag
from rooms.models import Room
from activities.models import UserActivityInfo
from .serializers import RoomSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# 방 생성
class RoomCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            room = serializer.save(master=request.user)

            # 태그 입력
            try:
                tag_names = request.data.get("tags")  # str을 가진 list 반환
            except tag_names.DoesNotExist():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            for tag_name in tag_names:
                tag = Tag.objects.get(tag_name=tag_name)
                serializer.instance.tags.add(tag)

            # 활동 태그 입력
            try:
                activity_tag_names = request.data.get("activity_tags")  # str을 가진 list 반환
            except activity_tag_names.DoesNotExists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            for activity_tag_name in activity_tag_names:
                activity_tag = ActivityTag.objects.get(tag_name=activity_tag_name)
                serializer.instance.activity_tags.add(activity_tag)

            # 방장의 보증금 확인
            if request.user.coin < room.deposit:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # 유저 활동 정보 생성
            user_activity_info = UserActivityInfo.objects.create(
                user=request.user,
                room=room,
                deposit_left=room.deposit
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

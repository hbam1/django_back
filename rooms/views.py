from django.shortcuts import render
from rest_framework import viewsets, status
from goals.models import Tag, ActivityTag
from rooms.models import Room
from .serializers import RoomSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 방장에 유저 저장
        serializer.save(master=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = RoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 태그 입력
        tag_names = request.data.get("tags")  # str을 가진 list 반환
        for tag_name in tag_names:
            tag = Tag.objects.get(tag_name=tag_name)
            serializer.instance.tags.add(tag)

        # 활동 태그 입력
        activity_tag_names = request.data.get("activity_tags")  # str을 가진 list 반환
        for activity_tag_name in activity_tag_names:
            activity_tag = ActivityTag.objects.get(tag_name=activity_tag_name)
            serializer.instance.activity_tags.add(activity_tag)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
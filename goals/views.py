from urllib import request
from rest_framework import viewsets, status
from .serializers import *
from goals.models import Goal
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

# 목표 viewset
class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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

    def perform_create(self, serializer):
        # 현재 유저를 저장
        serializer.save(user=self.request.user)


# 태그 조회
class TagListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tags = Tag.objects.all().order_by('-tag_name')
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 활동 태그 조회
class ActivityTagListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        activity_tags = ActivityTag.objects.all()
        serializer = ActivityTagSerializer(activity_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 방 생성 시 목표 조회
class GoalListAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 로그인된 유저 정보
        user = request.user
        # user가 생성한 목표 리스트
        goals = Goal.objects.filter(user=user).order_by('-title')
        serializer = GoalListSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

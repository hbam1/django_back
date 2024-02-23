from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", views.GoalViewSet)

urlpatterns = [
    # viewset이 위로 올라갔을 때 url이 꼬일 수 있는 것 주의
    path("tags/", views.TagListAPI.as_view()),
    path("activity_tags/", views.ActivityTagListAPI.as_view()),
    # 방 만들 때 필요한 목표 리스트
    path("lists/", views.GoalListAPI.as_view()),
    # 유저의 목표에 대한 추천 그룹 반환 API
    path('recommend_group/<int:goal_id>/', views.GroupRecommendationAPI.as_view()),
    path("", include(router.urls)),
]
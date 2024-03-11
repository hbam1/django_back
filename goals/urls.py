from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", views.GoalViewSet)

urlpatterns = [
    # viewset이 위로 올라갔을 때 url이 꼬일 수 있는 것 주의
    path("parent_tags/", views.ParentTagListAPI.as_view()), # 부모 tag
    path("subtags/<int:pk>", views.SubTagListAPI.as_view()), # 자식 tag
    path("activity_tags/", views.ActivityTagListAPI.as_view()), # 활동 tag
    # 유저의 목표에 대한 추천 그룹 반환 API
    path('<int:goal_id>/recommend_group/', views.GroupRecommendationAPI.as_view()),
    # 달성 보고
    path("achievement_reports/", views.AchievementReportAPI.as_view()),
    path("achievement_reports/create/<int:goal_id>/", views.AchievementReportCreateAPI.as_view()),
    path("achievement_reports/detail/<int:pk>/", views.AchievementReportDetailAPI.as_view()),
    # router 아래에 url을 작성하면 경로를 못찾음
    # goal 생성, 리스트 조회, 삭제
    path("", include(router.urls)),
]

from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", views.GoalViewSet)

urlpatterns = [
    # 유저의 전체 목표 리스트
    path('user_list/', views.UserGoalListAPI.as_view()),
    # viewset이 위로 올라갔을 때 url이 꼬일 수 있는 것 주의
    path("tags/", views.ParentTagListAPI.as_view()),
    path("subtags/<int:pk>", views.SubTagListAPI.as_view()),
    path("activity_tags/", views.ActivityTagListAPI.as_view()),
    # 유저의 목표에 대한 추천 그룹 반환 API
    path('recommend_group/<int:goal_id>/', views.GroupRecommendationAPI.as_view()),
    path("achievement_reports/", views.AchievementReportListAPI.as_view()),
    path("achievement_reports/<int:pk>/", views.AchievementReportDetailAPI.as_view()),
    path("achievement_reports/create/<int:goal_id>/", views.AchievementReportCreateAPI.as_view()),
    # router 아래에 url을 작성하면 경로를 못찾음
    path("", include(router.urls)),
]

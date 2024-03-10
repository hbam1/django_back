from django.urls import path, include
from . import views


urlpatterns = [
    # 방 만들 때 필요한 목표 리스트
    path("goal_list/", views.GoalListAPI.as_view()),
    # 방 리스트 조회 및 생성
    path("", views.RoomAPI.as_view()),
    # 방 detail
    path("<int:room_id>/", views.RoomGetAPI.as_view()),
    # 유저 추천
    path("<int:room_id>/recommend_members/", views.MemberRecommendationAPI.as_view()),
    # 방 활성화
    path("<int:room_id>/activate/", views.RoomActivateAPI.as_view()),
    # 방 활동종료
    path("<int:room_id>/close_room/", views.RoomClosureAPI.as_view()),
]
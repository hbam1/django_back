from django.urls import path, include
from . import views


urlpatterns = [
    # 방 만들 때 필요한 목표 리스트
    path("goal_list/", views.GoalListAPI.as_view()),
    path("room_list/", views.RoomListAPI.as_view()),
    path("create/", views.RoomCreateAPI.as_view()),
    path("<int:room_id>/", views.RoomGetAPI.as_view()),
    path("recommend_member/<int:room_id>/", views.MemberRecommendationAPI.as_view()),
    path("activate/<int:room_id>/", views.RoomActivateAPI.as_view()),
    path("close_room/<int:room_id>/", views.RoomClosureAPI.as_view()),
]
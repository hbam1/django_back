from django.urls import path, include
from . import views


urlpatterns = [
    path("create/", views.RoomCreateAPI.as_view()),
    path("recommend_member/<int:room_id>/", views.MemberRecommendationAPI.as_view()),
    path("activate/<int:room_id>/", views.RoomActivateAPI.as_view()),
]
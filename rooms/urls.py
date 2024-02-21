from django.urls import path, include
from . import views


urlpatterns = [
    path("create/", views.RoomCreateView.as_view()),
]
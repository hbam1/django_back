from django.urls import path, include
from . import views


urlpatterns = [
    path("create/", views.AlarmCreateAPI.as_view()),
    path("list/", views.AlarmListAPI.as_view()),
    path("retrieve/<int:pk>/", views.AlarmRetrieveAPI.as_view()),
    path("accept/<int:pk>/", views.AlarmAcceptAPI.as_view()),
    path("reject/<int:pk>", views.AlarmRejectAPI.as_view())
]
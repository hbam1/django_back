from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.AlarmAPI.as_view()),
    path("<int:alarm_id>/", views.AlarmRetrieveAPI.as_view()),
    path("<int:alarm_id>/accept/", views.AlarmAcceptAPI.as_view()),
    path("<int:alarm_id>/reject/", views.AlarmRejectAPI.as_view())
]
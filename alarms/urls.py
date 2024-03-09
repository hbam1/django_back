from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.AlarmAPI.as_view()),
    path("<int:pk>/", views.AlarmRetrieveAPI.as_view()),
    path("<int:pk>/accept/", views.AlarmAcceptAPI.as_view()),
    path("<int:pk>/reject/", views.AlarmRejectAPI.as_view())
]
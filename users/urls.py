from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("auth/", AuthAPIView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
]
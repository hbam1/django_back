from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterAPI.as_view()), # 회원가입
    path("auth/", AuthAPIView.as_view()), # 로그인
    path("auth/refresh/", TokenRefreshView.as_view()), # 토큰 재발급
    path("detail/", UserDetailAPI.as_view()), # 회원정보
    path("current/detail/", CurrentUserAPI.as_view()), #현재 로그인 회원정보
]
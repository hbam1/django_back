from django.urls import path, include
from rest_framework import routers

from .views import RegisterAPIView, AuthAPIView, UserViewSet

router = routers.DefaultRouter()
router.register('list', UserViewSet) # 유저리스트 (테스트용)

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("auth/", AuthAPIView.as_view()),
    path("", include(router.urls)),
]
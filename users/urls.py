from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register('list', UserViewSet) # 유저리스트 (테스트용)

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("auth/", AuthAPIView.as_view()),
    # 기능 테스트
    path("", include(router.urls)),
]
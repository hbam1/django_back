from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", views.FreeBoardViewSet, basename="activities")

urlpatterns = [
    path("create/", views.MemberAuthCreateAPI.as_view()),
    path("accept/<int:pk>/", views.MemberAuthAcceptAPI.as_view()),
    path("reject/<int:pk>/", views.MemberAuthRejectAPI.as_view()),
    path("list/", views.LogListAPI.as_view()),
    path("freeboard/", include(router.urls)),
]
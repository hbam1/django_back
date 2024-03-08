from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", views.FreeBoardViewSet, basename="activities")
router.register("", views.CommentViewSet, basename="activities")
router.register(r'authentications', views.AuthenticationViewSet)

urlpatterns = [
    path("member_list/", views.MemberListAPI.as_view()),
    path("create_auto_authentication/", views.CreateAutoAuthenticationAPI.as_view()),
    path("create/", views.MemberAuthCreateAPI.as_view()),
    path("auth_list/", views.AuthListAPI.as_view()),
    path("accept/<int:pk>/", views.MemberAuthAcceptAPI.as_view()),
    path("reject/<int:pk>/", views.MemberAuthRejectAPI.as_view()),
    path("auth_log_list/", views.LogListAPI.as_view()),
    path("freeboard/post/<int:post_id>/like/", views.LikePostAPI.as_view()),
    path("freeboard/comment/<int:comment_id>/like/", views.LikePostAPI.as_view()),
    path("freeboard/", include(router.urls)),
    path("freeboard/<int:post_id>/comment/", include(router.urls)),
    path('', include(router.urls)),
]
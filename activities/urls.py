from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", views.FreeBoardViewSet, basename="activities")
router.register("", views.CommentViewSet, basename="activities")
router.register(r'authentications', views.AuthenticationViewSet)

urlpatterns = [
    # 활동 멤버 조회
    path("member_list/", views.MemberListAPI.as_view()),
    # 인증 자동 생성 설정
    path("create_auto_authentication/", views.CreateAutoAuthenticationAPI.as_view()),
    # 멤버 인증 제출 및 리스트 조회
    path("member_authentication/", views.MemberAuthAPI.as_view()),
    # 방장의 인증 수락 및 거절
    path("member_authentication/<int:pk>/accept/", views.MemberAuthAcceptAPI.as_view()),
    path("member_authentication/<int:pk>/reject/", views.MemberAuthRejectAPI.as_view()),
    # 완료된 인증 로그 조회
    path("member_authentication/auth_log_list/", views.LogListAPI.as_view()),
    # 게시글 좋아요 및 댓글 좋아요
    path("freeboard/post/<int:post_id>/like/", views.LikePostAPI.as_view()),
    path("freeboard/comment/<int:comment_id>/like/", views.LikePostAPI.as_view()),
    path("freeboard/", include(router.urls)),
    path("freeboard/<int:post_id>/comment/", include(router.urls)),
    path('', include(router.urls)),
]
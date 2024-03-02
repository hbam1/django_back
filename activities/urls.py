from django.urls import path
from . import views
from tasks import *

urlpatterns = [
    path("create/", views.MemberAuthCreateAPI.as_view()),
    path("accept/<int:pk>/", views.MemberAuthAcceptAPI.as_view()),
    path("reject/<int:pk>/", views.MemberAuthRejectAPI.as_view()),
    path("list/<int:pk>/", views.LogListAPI.as_view()),
]
from django.db import models
from users.models import User
from rooms.models import Room
from django.utils import timezone


class UserActivityInfo(models.Model):
    user = models.ForeignKey(User, related_name='activity_infos', on_delete=models.CASCADE, help_text="유저")
    room = models.ForeignKey(Room, related_name='activity_infos', on_delete=models.CASCADE, help_text="방")
    deposit_left = models.PositiveIntegerField(default=None, null=True, blank=True, help_text="잔여 보증금")
    authentication_count = models.PositiveIntegerField(default=0, help_text="유효한 인증 횟수")


#그룹장이 만드는 인증 => 인증을 마감하는 시점에서 삭제
class Authentication(models.Model):
    room = models.ForeignKey(Room, related_name='room', on_delete=models.CASCADE, help_text="방")
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE, help_text="유저")
    start = models.DateTimeField(help_text="시작 시각")
    end = models.DateTimeField(help_text="종료 시각")
    participated = models.ManyToManyField(User, default=None, help_text="참가 유저")


#그룹에서 하는 인증 => 수락하는 시점에서 삭제
class MemberAuthentication(models.Model):
    room = models.ForeignKey(Room, related_name='auth_room', on_delete=models.CASCADE, help_text="방")
    user = models.ForeignKey(User, related_name='auth_user', on_delete=models.CASCADE, help_text="유저")
    is_auth = models.BooleanField(default=False, help_text="인증 성공 여부")
    content = models.CharField('내용', max_length=100, help_text="인증 내용")
    image = models.ImageField('사진', upload_to='authentication_images/', null=True, blank=True, help_text="인증 사진")
    is_completed = models.BooleanField(default=False, help_text="인증 완료 여부")
    created_date = models.DateTimeField(default=timezone.now, help_text="인증 생성 일자")

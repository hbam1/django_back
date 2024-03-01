from django.db import models
from users.models import User
from rooms.models import Room


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
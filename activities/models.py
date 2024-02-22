from django.db import models
from users.models import User
from rooms.models import Room


class UserActivityInfo(models.Model):
    user = models.ForeignKey(User, related_name='activity_infos', on_delete=models.CASCADE, help_text="유저")
    room = models.ForeignKey(Room, related_name='activity_infos', on_delete=models.CASCADE, help_text="방")
    deposit_left = models.PositiveIntegerField(default=None, null=True, blank=True, help_text="잔여 보증금")
    authentication_count = models.PositiveIntegerField(default=0, help_text="유효한 인증 횟수")
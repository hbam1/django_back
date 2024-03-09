from django.db import models
from users.models import User
from rooms.models import Room
from goals.models import Goal

# Create your models here.
class Alarm(models.Model):
    alarm_from = models.ForeignKey(User, related_name='sent_alarms', on_delete=models.CASCADE, help_text="발신자")
    alarm_to = models.ForeignKey(User, related_name='received_alarms', on_delete=models.CASCADE, help_text="수신자")
    #alarm 보낼때 room 정보 필요
    room = models.ForeignKey(Room, related_name='alarms', on_delete=models.CASCADE, null=True, blank=True, help_text="방")
    goal = models.ForeignKey(Goal, related_name='goals', on_delete=models.CASCADE, null=True, blank=True, help_text="목표")
    current_user_id = models.IntegerField(null=True, blank=True)
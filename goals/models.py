from django.db import models
from users.models import User

# 목표 태그
class Tag(models.Model):
    tag_name = models.CharField(max_length=10)
    parent_tag = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.tag_name

# 활동 태그
class ActivityTag(models.Model):
    tag_name = models.CharField(max_length=10)

    def __str__(self):
        return self.tag_name

# 목표
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goal', help_text="유저")
    tags = models.ManyToManyField(Tag, default=None, help_text="목표 태그")
    activity_tags = models.ManyToManyField(ActivityTag, default=None, help_text="활동 태그")
    title = models.CharField(max_length=50, help_text="목표 제목")
    content = models.TextField(help_text="목표 내용")
    favor_offline = models.BooleanField(default=False, help_text="대면 희망 여부")
    is_in_group = models.BooleanField(default=False, help_text="그룹 소속 여부")
    is_completed = models.BooleanField(default=False, help_text="목표 완료 여부")
    belonging_group_id = models.IntegerField(null=True, help_text="소속된 그룹")

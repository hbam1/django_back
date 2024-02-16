from django.db import models
from goals.models import Tag, ActivityTag
from users.models import User


class Room(models.Model):
    title = models.CharField(max_length=50, help_text="방 이름")
    detail = models.TextField(help_text="세부사항")
    members = models.ManyToManyField(User, related_name='members', default=None, help_text="그룹원")
    master = models.ForeignKey(User, related_name='master', on_delete=models.CASCADE, help_text="그룹장")
    # elastic search의 인덱스를 간단하게 만들기 위해서 조치가 필요
    # 따라서 master의 goal list를 보내준 다음, 선택한 goal의 tag들을 값으로 넘겨줌
    tags = models.ManyToManyField(Tag, default=None, help_text="태그")
    activity_tags = models.ManyToManyField(ActivityTag, default=None, help_text="활동 태그")
    cert_required = models.BooleanField(default=False, help_text="인증 필수 여부")
    cert_detail = models.TextField(null=True, help_text="인증 상세")
    penalty_value = models.PositiveIntegerField(default=0, help_text="벌금")
    favor_offline = models.BooleanField(default=False, help_text="대면활동 유무")
    is_active = models.BooleanField(default=False, help_text="활성화 여부")

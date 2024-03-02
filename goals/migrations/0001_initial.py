# Generated by Django 4.2.10 on 2024-03-02 08:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tag_name", models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tag_name", models.CharField(max_length=10)),
                (
                    "parent_tag",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="goals.tag",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Goal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(help_text="목표 제목", max_length=50)),
                ("content", models.TextField(help_text="목표 내용")),
                (
                    "favor_offline",
                    models.BooleanField(default=False, help_text="대면 희망 여부"),
                ),
                (
                    "is_in_group",
                    models.BooleanField(default=False, help_text="그룹 소속 여부"),
                ),
                (
                    "is_completed",
                    models.BooleanField(default=False, help_text="목표 완료 여부"),
                ),
                (
                    "belonging_group_id",
                    models.IntegerField(help_text="소속된 그룹", null=True),
                ),
                (
                    "activity_tags",
                    models.ManyToManyField(
                        default=None, help_text="활동 태그", to="goals.activitytag"
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        default=None, help_text="목표 태그", to="goals.tag"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="유저",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="goal",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AchievementReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField()),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="달성보고 이미지",
                        null=True,
                        upload_to="achievement_reports/",
                    ),
                ),
                (
                    "goal",
                    models.ForeignKey(
                        help_text="목표",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="goals.goal",
                    ),
                ),
                (
                    "reacted_dislike",
                    models.ManyToManyField(
                        default=None,
                        help_text="싫어요",
                        related_name="disliked_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reacted_love",
                    models.ManyToManyField(
                        default=None,
                        help_text="찜하기",
                        related_name="loved_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reacted_respectful",
                    models.ManyToManyField(
                        default=None,
                        help_text="좋아요",
                        related_name="respected_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

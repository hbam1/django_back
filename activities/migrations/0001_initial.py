# Generated by Django 4.2.10 on 2024-03-02 04:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserActivityInfo",
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
                (
                    "deposit_left",
                    models.PositiveIntegerField(
                        blank=True, default=None, help_text="잔여 보증금", null=True
                    ),
                ),
                (
                    "authentication_count",
                    models.PositiveIntegerField(default=0, help_text="유효한 인증 횟수"),
                ),
                (
                    "room",
                    models.ForeignKey(
                        help_text="방",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_infos",
                        to="rooms.room",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="유저",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_infos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MemberAuthentication",
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
                ("is_auth", models.BooleanField(default=False, help_text="인증 성공 여부")),
                (
                    "content",
                    models.CharField(
                        help_text="인증 내용", max_length=100, verbose_name="내용"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="인증 사진",
                        null=True,
                        upload_to="authentication_images/",
                        verbose_name="사진",
                    ),
                ),
                (
                    "is_completed",
                    models.BooleanField(default=False, help_text="인증 완료 여부"),
                ),
                (
                    "created_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now, help_text="인증 생성 일자"
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        help_text="방",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auth_room",
                        to="rooms.room",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="유저",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auth_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Authentication",
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
                ("start", models.DateTimeField(help_text="시작 시각")),
                ("end", models.DateTimeField(help_text="종료 시각")),
                (
                    "participated",
                    models.ManyToManyField(
                        default=None, help_text="참가 유저", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        help_text="방",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="room",
                        to="rooms.room",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="유저",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

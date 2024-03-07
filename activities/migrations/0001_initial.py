# Generated by Django 4.2.10 on 2024-03-06 09:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
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
            ],
        ),
        migrations.CreateModel(
            name="Comment",
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
                ("content", models.TextField(help_text="내용")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, help_text="생성일자"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, help_text="수정일자", null=True),
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
            ],
        ),
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(help_text="제목", max_length=200, null=True)),
                ("content", models.TextField(help_text="내용")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, help_text="생성일자"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, help_text="수정일자", null=True),
                ),
                ("notice", models.BooleanField(default=False, help_text="공지")),
            ],
        ),
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
            ],
        ),
    ]

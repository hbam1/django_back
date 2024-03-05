# Generated by Django 4.2.10 on 2024-03-05 04:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rooms", "0004_alter_room_cert_detail"),
        ("activities", "0001_initial"),
    ]

    operations = [
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
                (
                    "author",
                    models.ForeignKey(
                        help_text="작성자",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author_post",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        help_text="방",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="room_posts",
                        to="rooms.room",
                    ),
                ),
                (
                    "voter",
                    models.ManyToManyField(
                        help_text="추천인",
                        related_name="voter_post",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
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
                (
                    "author",
                    models.ForeignKey(
                        help_text="작성자",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author_comment",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        help_text="게시물",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="activities.post",
                    ),
                ),
                (
                    "voter",
                    models.ManyToManyField(
                        help_text="추천인",
                        related_name="voter_comment",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

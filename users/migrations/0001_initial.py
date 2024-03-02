# Generated by Django 4.2.10 on 2024-03-02 08:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(help_text="이메일", max_length=254, unique=True),
                ),
                (
                    "nickname",
                    models.CharField(
                        blank=True,
                        help_text="닉네임",
                        max_length=30,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "profile",
                    models.CharField(
                        blank=True, help_text="소개글", max_length=255, null=True
                    ),
                ),
                (
                    "profile_image",
                    models.ImageField(
                        blank=True,
                        help_text="프로필 이미지",
                        null=True,
                        upload_to="profile_images/%Y/%m/%d/",
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True, help_text="사는 도시", max_length=30, null=True
                    ),
                ),
                (
                    "region_detail",
                    models.CharField(
                        blank=True, help_text="상세 주소", max_length=30, null=True
                    ),
                ),
                (
                    "fuel",
                    models.FloatField(
                        blank=True,
                        default=0,
                        help_text="연료",
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("new", models.BooleanField(default=True, help_text="신규 회원")),
                ("coin", models.PositiveIntegerField(default=5000, help_text="재화")),
                ("is_superuser", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

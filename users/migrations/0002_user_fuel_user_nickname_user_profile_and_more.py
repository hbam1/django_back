# Generated by Django 5.0.2 on 2024-02-11 15:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="fuel",
            field=models.PositiveIntegerField(
                blank=True, default=100, help_text="연료", null=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="nickname",
            field=models.CharField(
                blank=True, help_text="닉네임", max_length=30, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="profile",
            field=models.CharField(
                blank=True, help_text="프로필 글", max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="profile_image",
            field=models.CharField(
                blank=True, help_text="프로필 사진", max_length=150, null=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="region",
            field=models.CharField(
                blank=True, help_text="사는 도시", max_length=30, null=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="region_detail",
            field=models.CharField(
                blank=True, help_text="상세 주소", max_length=30, null=True
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(help_text="이메일", max_length=254, unique=True),
        ),
    ]

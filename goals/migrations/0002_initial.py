# Generated by Django 5.0.2 on 2024-03-05 14:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('goals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='achievementreport',
            name='reacted_dislike',
            field=models.ManyToManyField(default=None, help_text='싫어요', related_name='disliked_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievementreport',
            name='reacted_love',
            field=models.ManyToManyField(default=None, help_text='찜하기', related_name='loved_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievementreport',
            name='reacted_respectful',
            field=models.ManyToManyField(default=None, help_text='좋아요', related_name='respected_reports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='goal',
            name='activity_tags',
            field=models.ManyToManyField(default=None, help_text='활동 태그', to='goals.activitytag'),
        ),
        migrations.AddField(
            model_name='goal',
            name='user',
            field=models.ForeignKey(help_text='유저', on_delete=django.db.models.deletion.CASCADE, related_name='goal', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievementreport',
            name='goal',
            field=models.ForeignKey(help_text='목표', on_delete=django.db.models.deletion.CASCADE, to='goals.goal'),
        ),
        migrations.AddField(
            model_name='tag',
            name='parent_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='goals.tag'),
        ),
        migrations.AddField(
            model_name='goal',
            name='tags',
            field=models.ManyToManyField(default=None, help_text='목표 태그', to='goals.tag'),
        ),
    ]
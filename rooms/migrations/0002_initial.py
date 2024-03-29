# Generated by Django 5.0.3 on 2024-03-10 08:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('goals', '0002_initial'),
        ('rooms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='master',
            field=models.ForeignKey(help_text='그룹장', on_delete=django.db.models.deletion.CASCADE, related_name='master', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='members',
            field=models.ManyToManyField(default=None, help_text='그룹원', related_name='members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='tags',
            field=models.ManyToManyField(default=None, help_text='태그', to='goals.tag'),
        ),
    ]

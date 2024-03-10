# Generated by Django 5.0.3 on 2024-03-10 08:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alarms', '0001_initial'),
        ('goals', '0001_initial'),
        ('rooms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='alarm_from',
            field=models.ForeignKey(help_text='발신자', on_delete=django.db.models.deletion.CASCADE, related_name='sent_alarms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='alarm',
            name='alarm_to',
            field=models.ForeignKey(help_text='수신자', on_delete=django.db.models.deletion.CASCADE, related_name='received_alarms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='alarm',
            name='goal',
            field=models.ForeignKey(blank=True, help_text='목표', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='goals.goal'),
        ),
        migrations.AddField(
            model_name='alarm',
            name='room',
            field=models.ForeignKey(blank=True, help_text='방', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alarms', to='rooms.room'),
        ),
    ]

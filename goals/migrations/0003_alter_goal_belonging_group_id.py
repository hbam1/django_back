# Generated by Django 5.0.2 on 2024-02-16 09:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("goals", "0002_rename_activitytags_goal_activity_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goal",
            name="belonging_group_id",
            field=models.IntegerField(help_text="소속된 그룹", null=True),
        ),
    ]

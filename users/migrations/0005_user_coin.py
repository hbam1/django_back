# Generated by Django 5.0.2 on 2024-02-24 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_user_new"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="coin",
            field=models.PositiveIntegerField(default=5000, help_text="재화"),
        ),
    ]

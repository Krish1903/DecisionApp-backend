# Generated by Django 3.2.2 on 2023-08-19 14:22

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0004_auto_20230819_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 26, 14, 22, 37, 624379, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='expo_push_token',
            field=models.JSONField(blank=True, default=list),
        ),
    ]

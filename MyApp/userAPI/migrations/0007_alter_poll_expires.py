# Generated by Django 3.2.2 on 2023-10-09 16:16

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0006_auto_20231009_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 16, 16, 16, 50, 283971, tzinfo=utc)),
        ),
    ]
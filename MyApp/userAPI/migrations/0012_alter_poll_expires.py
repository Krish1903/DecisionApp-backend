# Generated by Django 3.2.2 on 2023-07-19 05:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0011_auto_20230708_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 26, 5, 8, 24, 917293, tzinfo=utc)),
        ),
    ]

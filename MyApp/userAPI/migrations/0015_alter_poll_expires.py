# Generated by Django 3.2.2 on 2023-07-24 10:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0014_alter_poll_expires'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 31, 10, 0, 47, 893230, tzinfo=utc)),
        ),
    ]

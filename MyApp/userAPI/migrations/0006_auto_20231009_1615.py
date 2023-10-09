# Generated by Django 3.2.2 on 2023-10-09 16:15

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0005_auto_20230819_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='blocked_users',
            field=models.ManyToManyField(related_name='blocked_by', to='userAPI.UserAccount'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 16, 16, 15, 28, 414924, tzinfo=utc)),
        ),
    ]

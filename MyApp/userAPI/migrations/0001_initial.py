# Generated by Django 3.2.2 on 2023-08-19 14:10

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires', models.DateTimeField(default=datetime.datetime(2023, 8, 26, 14, 10, 13, 297396, tzinfo=utc))),
                ('image_url', models.URLField(blank=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_polls', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expo_push_tokens', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile_picture', models.URLField(blank=True)),
                ('bio', models.CharField(blank=True, max_length=300)),
                ('following', models.ManyToManyField(related_name='followers', to='userAPI.UserAccount')),
                ('interacted_polls', models.ManyToManyField(related_name='interacted_users', to='userAPI.Poll')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=200)),
                ('image_url', models.URLField(blank=True)),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='userAPI.poll')),
                ('votes', models.ManyToManyField(related_name='voted_options', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notification_type', models.CharField(max_length=200)),
                ('source_id', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

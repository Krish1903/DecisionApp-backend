from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


import uuid

# Create your models here


class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, related_name='created_polls', on_delete=models.CASCADE, null=True)
    expires = models.DateTimeField(default=timezone.now() + timedelta(days=7))


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=200)
    poll = models.ForeignKey(
        Poll, related_name='options', on_delete=models.CASCADE)
    votes = models.ManyToManyField(User, related_name='voted_options')


class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interacted_polls = models.ManyToManyField(
        Poll, related_name='interacted_users')
    created_at = models.DateTimeField(auto_now_add=True)

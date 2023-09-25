from django.db import models

from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from exponent_server_sdk import PushClient, PushMessage

import uuid

# Create your models here


class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, related_name='created_polls', on_delete=models.CASCADE, null=True)
    expires = models.DateTimeField(default=timezone.now() + timedelta(days=7))
    image_url = models.URLField(blank=True)
    flagged = models.BooleanField(default=False)



class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=200)
    poll = models.ForeignKey(
        Poll, related_name='options', on_delete=models.CASCADE)
    votes = models.ManyToManyField(User, related_name='voted_options')
    image_url = models.URLField(blank=True)


class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expo_push_token = models.JSONField(blank=True, default=list)
    interacted_polls = models.ManyToManyField(
        Poll, related_name='interacted_users')
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.URLField(blank=True)
    bio = models.CharField(max_length=300, blank=True)
    following = models.ManyToManyField(
        'self', related_name='followers', symmetrical=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserAccount.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.useraccount.save()

    def notify_new_follower(self, follower_username):
        for token in self.expo_token:
            message = PushMessage(
                to=token, 
                body=f'You have been followed by {follower_username}!')
            response = PushClient().publish(message)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=200)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=200)  # Could be 'follower' or 'vote'
    source_id = models.CharField(max_length=200)  # id of the user who followed or the poll voted on

    def mark_as_read(self):
        self.read = True
        self.save()

    class Meta:
        ordering = ['-created_at']

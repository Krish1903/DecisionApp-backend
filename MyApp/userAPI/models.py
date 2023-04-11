from django.db import models
from django.contrib.auth.models import User

# Create your models here


class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class Answer(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text

# represents a user's choice in a poll


class Choice(models.Model):
    # uses foreign keys for the user, the poll, and the answer.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.poll.question} - {self.answer.text}"

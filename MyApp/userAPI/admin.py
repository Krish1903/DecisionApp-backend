from django.contrib import admin
from .models import Poll, Option, UserAccount, Notification

admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(UserAccount)
admin.site.register(Notification)
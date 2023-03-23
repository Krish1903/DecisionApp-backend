from django.urls import path
from .views import TestView

urlpatterns = [
    path("test", TestView.as_view()),
]


# access each view
# localhost:8000/api/v1.0/user/"..."

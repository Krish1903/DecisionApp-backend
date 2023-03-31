from django.urls import path
from .views import TestView, UsersView, UserLoginView, HardcodedUserView

urlpatterns = [
    path("test", TestView.as_view()),
    path("create-user/", UsersView.as_view()),
    path("get-user", UserLoginView.as_view()),
    path('login-user/', UserLoginView.as_view()),
    path('hardcoded-user/', HardcodedUserView.as_view(), name='hardcoded-user')
]


# access each view
# localhost:8000/api/v1.0/user/"..."

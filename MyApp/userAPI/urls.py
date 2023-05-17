from django.urls import path
from . import views

urlpatterns = [
    path("test", views.TestView.as_view()),
    path("create-user/", views.UsersView.as_view()),
    path("get-user/", views.UserLoginView.as_view()),
    path('login-user/', views.UserLoginView.as_view()),
    path("user-profile/", views.UserAccountView.as_view()),
    path("create-poll/", views.PollsView.as_view()),
    path("create-option/", views.OptionsView.as_view()),
]


# access each view
# localhost:8000/api/v1.0/user/"..."

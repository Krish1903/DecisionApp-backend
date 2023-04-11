from django.urls import path
from . import views

urlpatterns = [
    path("test", views.TestView.as_view()),
    path("create-user/", views.UsersView.as_view()),
    path("get-user/", views.UserLoginView.as_view()),
    path('login-user/', views.UserLoginView.as_view()),
    path('polls/', views.PollList.as_view(), name='poll-list'),
    path('polls/<int:pk>/', views.PollDetail.as_view(), name='poll-detail'),
    path('answers/', views.AnswerList.as_view(), name='answer-list'),
    path('answers/<int:pk>/', views.AnswerDetail.as_view(), name='answer-detail'),
    path('choices/', views.ChoiceList.as_view(), name='choice-list'),
    path('choices/<int:pk>/', views.ChoiceDetail.as_view(), name='choice-detail'),
]


# access each view
# localhost:8000/api/v1.0/user/"..."

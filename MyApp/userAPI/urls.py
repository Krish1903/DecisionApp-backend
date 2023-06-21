from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("test", views.TestView.as_view()),
    path('admin/', admin.site.urls),
    path("create-user/", views.UsersView.as_view()),
    path("get-user/", views.UserLoginView.as_view()),
    path('login-user/', views.UserLoginView.as_view()),
    path("user-profile/", views.UserAccountView.as_view()),
    path("create-poll/", views.PollsView.as_view()),
    path("get-polls/", views.PollsView.as_view()),
    path("get-active-polls/", views.ActivePollsView.as_view()),
    path("create-option/", views.OptionsView.as_view()),
    path('login-google/', views.GoogleLoginView.as_view()),
    path('login-facebook/', views.FacebookLoginView.as_view(), name='login-facebook'),
    path('options/<uuid:option_id>/vote/',
         views.VoteView.as_view(), name='vote'),
    path("get-user-profile/<int:user_id>/", views.UserProfileView.as_view()),
    path('follow/', views.FollowView.as_view(), name='follow'),
    path('unfollow/', views.UnfollowView.as_view(), name='unfollow'),
    path('get-friends/<str:ids>/',
         views.GetFriendsView.as_view()),

]


# access each view
# localhost:8000/api/v1.0/user/"..."

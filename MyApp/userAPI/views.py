from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer, PollSerializer, OptionSerializer, UserAccountSerializer, GoogleUserSerializer

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import Poll, UserAccount, Option, GoogleUser

from rest_framework.pagination import LimitOffsetPagination

# Create your views here.


class TestView(APIView):
    # getting information from the server
    def get(self, request, format=None):
        print("API was Called")
        return Response("You Made It", status=200)

    # send something to django create object
    # def post():
        # ...

    # send something to django to update and already created object
    # def put():
        # ...


class UsersView(APIView):

    def post(self, request, format=None):
        print("Creating a user")

        user_data = request.data
        print(request.data)
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid(raise_exception=False):
            user_serializer.save()
            return Response(user_serializer.data, status=200)

        print(user_serializer.errors)
        return Response({"msg": "ERR in API"}, status=400)


class UserLoginView(APIView):
    # Convert a user token into user data
    def get(self, request, format=None):

        if request.user.is_authenticated == False or request.user.is_active == False:
            return Response("Invalid Credentials", status=403)

        user = UserSerializer(request.user)
        return Response(user.data, status=200)

    def post(self, request, format=None):
        print("Login Class")

        user_obj = User.objects.filter(email=request.data['username']).first(
        ) or User.objects.filter(username=request.data['username']).first()

        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': request.data['password']
            }
            user = authenticate(**credentials)

            if user and user.is_active:
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data, status=200)

        return Response("Invalid Credentials", status=403)


class UserAccountView(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response("Invalid Credentials", status=403)

        profile = UserAccount.objects.get(user=request.user)
        serializer = UserAccount(profile)
        return Response(serializer.data, status=200)

    def put(self, request, format=None):
        if not request.user.is_authenticated:
            return Response("Invalid Credentials", status=403)

        profile = UserAccount.objects.get(user=request.user)
        data = {
            'bio': request.data.get('bio', profile.bio),
            'profile_picture': request.data.get('profile_picture', profile.profile_picture)
        }
        serializer = UserAccountSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, format=None):
        if not request.user.is_authenticated:
            return Response("Invalid Credentials", status=403)

        user = request.user
        user.delete()
        return Response({"msg": "User account successfully deleted"}, status=200)


class PollsView(APIView):
    def post(self, request, format=None):
        poll_data = request.data
        poll_serializer = PollSerializer(data=poll_data)
        if poll_serializer.is_valid():
            poll_serializer.save()
            return Response({"poll": poll_serializer.data}, status=200)
        return Response({"msg": "ERR with poll data"}, status=400)


class OptionsView(APIView):
    def post(self, request, format=None):
        option_data = request.data
        option_serializer = OptionSerializer(data=option_data)
        if option_serializer.is_valid():
            option_serializer.save()
            return Response({"option": option_serializer.data}, status=200)
        return Response({"msg": "ERR with option data"}, status=400)

    def put(self, request, format=None):
        if 'id' not in request.data:
            return Response("Option id is missing", status=400)

        try:
            option = Option.objects.get(id=request.data['id'])
        except Option.DoesNotExist:
            return Response("Option not found", status=404)

        serializer = OptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class FollowersPollsView(APIView):
    pagination_class = LimitOffsetPagination

    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response("Invalid Credentials", status=403)

        user_account = UserAccount.objects.get(user=request.user)
        followers_polls = Poll.objects.filter(
            owner__useraccount__in=user_account.followers.all()).order_by('expires')
        page = self.pagination_class.paginate_queryset(
            followers_polls, request)
        serializer = PollSerializer(page, many=True)
        return self.pagination_class.get_paginated_response(serializer.data)


class GoogleLoginView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data.get('email')
        full_name = request.data.get('name')
        profile_picture = request.data.get('picture')

        try:
            user = User.objects.get(email=email)
            try:
                user.useraccount.profile_picture = profile_picture
                user.useraccount.save()
            except User.useraccount.RelatedObjectDoesNotExist:
                UserAccount.objects.create(
                    user=user, profile_picture=profile_picture)

        except User.DoesNotExist:
            # Create new user and UserAccount if User does not exist
            user = User(email=email)
            user.username = email.split('@')[0]
            user.set_unusable_password()
            user.first_name, user.last_name = self._get_name(full_name)
            user.save()

            UserAccount.objects.create(
                user=user, profile_picture=profile_picture)

        except User.MultipleObjectsReturned:
            # If there are multiple Users with the same email, log in the first one
            user = User.objects.filter(email=email).first()
            try:
                user.useraccount.profile_picture = profile_picture
                user.useraccount.save()
            except User.useraccount.RelatedObjectDoesNotExist:
                UserAccount.objects.create(
                    user=user, profile_picture=profile_picture)

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=200)

    def _get_name(self, full_name):
        parts = full_name.split(' ')
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name


class FacebookLoginView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data.get('email')
        full_name = request.data.get('name')
        profile_picture = request.data.get('picture').get('data').get('url')

        try:
            user = User.objects.get(email=email)
            try:
                user.useraccount.profile_picture = profile_picture
                user.useraccount.save()
            except User.useraccount.RelatedObjectDoesNotExist:
                UserAccount.objects.create(
                    user=user, profile_picture=profile_picture)

        except User.DoesNotExist:
            # Create new user and UserAccount if User does not exist
            user = User(email=email)
            user.username = email.split('@')[0]
            user.set_unusable_password()
            user.first_name, user.last_name = self._get_name(full_name)
            user.save()

            UserAccount.objects.create(
                user=user, profile_picture=profile_picture)

        except User.MultipleObjectsReturned:
            # If there are multiple Users with the same email, log in the first one
            user = User.objects.filter(email=email).first()
            try:
                user.useraccount.profile_picture = profile_picture
                user.useraccount.save()
            except User.useraccount.RelatedObjectDoesNotExist:
                UserAccount.objects.create(
                    user=user, profile_picture=profile_picture)

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=200)

    def _get_name(self, full_name):
        parts = full_name.split(' ')
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

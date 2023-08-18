from exponent_server_sdk import DeviceNotRegisteredError, PushClient, PushMessage, PushServerError, PushTicketError

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, PollSerializer, OptionSerializer, UserAccountSerializer, FriendsSerializer, NotificationSerializer, UserAccountFriendsSerializer

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import Poll, UserAccount, Option, Notification

from django.utils import timezone

from rest_framework.pagination import LimitOffsetPagination

from exponent_server_sdk import DeviceNotRegisteredError, PushClient, PushMessage

from requests.exceptions import ConnectionError, HTTPError

from django.db.models import Q

# Create your views here.


class TestPushNotifications(APIView):
    def post(self, request, format=None):
        return Response("Hi")

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

        if not request.user.is_authenticated or not request.user.is_active:
            return Response("Invalid Credentials", status=403)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

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
            # Check if the token is the same
            expo_push_token = request.data.get('expo_push_token')
            if expo_push_token and expo_push_token not in user.useraccount.expo_push_token:
                user.useraccount.expo_push_token.append(expo_push_token)
                user.useraccount.save()

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
            
            # Access the poll instance that has been saved.
            poll = poll_serializer.instance
            followers = poll.owner.useraccount.followers.all()

            push_client = PushClient()
            message_body = f"{poll.owner.username} on the fence about something"
            message_body1 = f"{poll.owner.username} just made a poll, pick something: '{poll.question}'"

            for follower in followers:
                if follower.expo_push_token:
                    notification_data = {
                        "type": "poll",
                        "source_id": str(poll.id)
                    }
                    try:
                        push_client.publish(PushMessage(
                            to=follower.expo_push_token,
                             body=message_body1))
                    except (PushServerError, ConnectionError, HTTPError, DeviceNotRegisteredError) as e:
                        print(e)

            return Response("success", status=201)

        return Response({"Err": poll_serializer.errors}, status=400)

    def get(self, request, format=None):
        polls = Poll.objects.all()
        serializer = PollSerializer(polls, many=True)
        return Response(serializer.data)


class ActivePollsView(APIView):
    def get(self, request, format=None):
        active_polls = Poll.objects.filter(
            expires__gt=timezone.now()).order_by('expires')
        serializer = PollSerializer(active_polls, many=True)
        return Response(serializer.data)

class SinglePollView(APIView):
    def get(self, request, *args, **kwargs):
        poll_id = kwargs.get('id') 
        poll = get_object_or_404(Poll, id=poll_id)
        serializer = PollSerializer(poll)
        return Response(serializer.data)

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
            # Try to get user by email
            user = User.objects.get(email=email)
            
        except User.MultipleObjectsReturned:
            # If multiple users, get the first one
            user = User.objects.filter(email=email).first()
            
        except User.DoesNotExist:
            # If user does not exist, create one
            user = User(email=email)
            user.username = email.split('@')[0]
            user.set_unusable_password()
            user.first_name, user.last_name = self._get_name(full_name)
            user.save()
        
        # Try to get or create UserAccount for this user
        user_account, created = UserAccount.objects.get_or_create(
            user=user, 
            defaults={'profile_picture': profile_picture}
        )
        
        # If UserAccount already existed and profile_picture is updated, save it
        if not created and profile_picture:
            user_account.profile_picture = profile_picture
            user_account.save()
            
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
            # create new user and UserAccount if User does not exist
            user = User(email=email)
            user.username = email.split('@')[0]
            user.set_unusable_password()
            user.first_name, user.last_name = self._get_name(full_name)
            user.save()

            UserAccount.objects.create(
                user=user, profile_picture=profile_picture)

        except User.MultipleObjectsReturned:
            # if there are multiple Users with the same email, log in the first one
            user = User.objects.filter(email=email).first()
            try:
                if profile_picture and not user.useraccount.profile_picture:
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


class VoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        option_id = kwargs.get('option_id')
        option = get_object_or_404(Option, id=option_id)
        poll = option.poll

        for opt in poll.options.all():
            if request.user in opt.votes.all():
                return Response({'err': 'You have already voted in this poll.'}, status=400)

        if request.user == poll.owner:
            return Response({'err': 'You cannot vote on your own poll.'}, status=400)

        option.votes.add(request.user)
        option.save()

        message_body = f"{request.user.username} just voted on your poll"
        message_body1 = f"{request.user.username} just picked something: '{poll.question}'"

        notification_data = {
            "type": "vote",
            "source_id": str(poll.id)
        }

        if poll.owner.useraccount.expo_push_token:
            push_client = PushClient()
            try:
                push_client.publish(PushMessage(
                    to=poll.owner.useraccount.expo_push_token, 
                    body=message_body,
                    data=notification_data
                ))
            except (PushServerError, ConnectionError, HTTPError, DeviceNotRegisteredError) as e:
                print(e)

        # Create a notification for the owner of the poll
        notification = Notification(
            user=poll.owner,  
            message=message_body1,
            notification_type="vote",
            source_id=str(poll.id),
            created_at=timezone.now(),
            read=False
        )
        notification.save()

        poll_serializer = PollSerializer(poll)

        return Response(poll_serializer.data, status=200)



class UserProfileView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response("User not found", status=404)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class FollowView(APIView):
    def post(self, request, *args, **kwargs):
        follower_id = request.data.get('follower_id')
        following_id = request.data.get('following_id')

        try:
            follower = User.objects.get(id=follower_id)
            following = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response({"msg": "User does not exist"}, status=404)

        follower.useraccount.following.add(following.useraccount)
        follower.useraccount.save()

        message_body = f"{follower.username} started following you"

        if following.useraccount.expo_push_token:
            push_client = PushClient()
            notification_data = {
                "type": "follow",
                "source_id": request.user.id
            }
            try:
                push_client.publish(PushMessage(
                    to=following.useraccount.expo_push_token, 
                    body=message_body,
                    data=notification_data
                ))
            except (PushServerError, ConnectionError, HTTPError, DeviceNotRegisteredError) as e:
                print(e)

        # Create a notification for the followed user
        notification = Notification(
            user=following,
            message=message_body,
            notification_type="follow",
            source_id=str(follower.id),
            created_at=timezone.now(),
            read=False
        )
        notification.save()

        serializer = UserSerializer(follower)

        return Response({"msg": "success"}, status=200)



class UnfollowView(APIView):
    def post(self, request, *args, **kwargs):
        unfollower_id = request.data.get('unfollower_id')
        unfollowing_id = request.data.get('unfollowing_id')

        try:
            follower = User.objects.get(id=unfollower_id)
            following = User.objects.get(id=unfollowing_id)
        except User.DoesNotExist:
            return Response({"msg": "User does not exist"}, status=404)

        follower.useraccount.following.remove(following.useraccount)
        follower.useraccount.save()

        serializer = UserSerializer(follower)

        return Response({"msg": "success"}, status=200)


class GetFriendsView(APIView):
    def get(self, request, ids, format=None):
        ids_list = ids.split(',')

        users = User.objects.filter(id__in=ids_list)
        serializer = FriendsSerializer(users, many=True)

        return Response(serializer.data, status=200)

class GetFollowers(APIView):
    def get(self, request, user_id, format=None):
        try: 
            user = get_object_or_404(User, id=user_id)
        except User.DoesNotExist:
            return Response("User not found.")

        followers = user.useraccount.followers.all()
        serializer = UserAccountFriendsSerializer(followers, many=True)

        return Response(serializer.data, status=200)


class GetFollowing(APIView):
    def get(self, request, user_id, format=None):
        try: 
            user = get_object_or_404(User, id=user_id)
        except User.DoesNotExist:
            return Response("User not found.")

        following = user.useraccount.following.all()
        serializer = UserAccountFriendsSerializer(following, many=True)

        return Response(serializer.data, status=200)
        
class ActivePollsFromFollowedUsersView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user_account = UserAccount.objects.get(user__id=user_id)
        except UserAccount.DoesNotExist:
            return Response("User not found.")

        followed_users = [
            ua.user for ua in user_account.following.all() if ua.user != user_account.user]

        active_polls = Poll.objects.filter(
            owner__in=followed_users,
            expires__gt=timezone.now()
        ).order_by('expires')

        serializer = PollSerializer(active_polls, many=True)
        return Response(serializer.data)


class ActivePollsFromNonFollowedUsersView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user_account = UserAccount.objects.get(user__id=user_id)
        except UserAccount.DoesNotExist:
            return Response("User not found.")

        followed_users = [ua.user for ua in user_account.following.all()]

        active_polls = Poll.objects.filter(
            expires__gt=timezone.now()
        ).exclude(
            owner__in=followed_users
        ).exclude(
            owner=user_account.user
        ).order_by('expires')

        serializer = PollSerializer(active_polls, many=True)
        return Response(serializer.data)


class UserPollsView(APIView):
    def get(self, request, user_id, format=None):
        user = get_object_or_404(User, id=user_id)

        user_polls = Poll.objects.filter(owner=user)

        serializer = PollSerializer(user_polls, many=True)
        return Response(serializer.data)

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):        
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        notifications = Notification.objects.filter(user=request.user)
        
        serializer = NotificationSerializer(notifications, many=True)

        return Response(serializer.data, status=200)

class VotedPollsView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)

        polls = Poll.objects.filter(
            options__votes__in=[user]
        ).exclude(owner=user).distinct()

        serializer = PollSerializer(polls, many=True)

        return Response(serializer.data, status=200)

class UserSearchView(APIView):
    def get(self, request, search_string=None, *args, **kwargs):
        current_user = request.user
        followed_users = []

        if hasattr(current_user, 'useraccount'):
            followed_users = current_user.useraccount.following.all().values_list('user__id', flat=True)

        base_query = User.objects.exclude(id=current_user.id) if current_user.is_authenticated else User.objects.all()

        if search_string:
            users = base_query.filter(
                Q(username__icontains=search_string) |
                Q(first_name__icontains=search_string) |
                Q(last_name__icontains=search_string)
            ).exclude(id__in=followed_users)

            if not users.exists():
                return Response([], status=200)
        else:
            users = base_query.order_by('first_name').exclude(id__in=followed_users)

        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data, status=200)
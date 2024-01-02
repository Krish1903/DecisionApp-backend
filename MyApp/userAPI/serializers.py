from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Poll, UserAccount, Option, Notification

class UserSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    expo_push_token = serializers.JSONField(required=False, write_only=True)
    full_name = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    profile_picture = serializers.URLField(
        source='useraccount.profile_picture', required=False)
    bio = serializers.CharField(source='useraccount.bio', required=False)

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        max_length=32,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True
    )
    blocked_users = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'full_name',
            'token',
            'profile_picture',
            'bio',
            'first_name',
            'last_name',
            "following",
            "followers",
            "expo_push_token",
            "blocked_users",
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        expo_push_token = validated_data.pop('expo_push_token', None)
        password = validated_data.pop('password', None)
        full_name = validated_data.pop('full_name', None)
        if full_name:
            first_name, last_name = self.split_full_name(full_name)
            validated_data['first_name'] = first_name
            validated_data['last_name'] = last_name
        user = User(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()

        # If an expo_push_token is provided, save it to the user's UserAccount
        if expo_push_token is not None:
            user_account = UserAccount.objects.get(user=user)
            if user_account.expo_push_token is None:
                user_account.expo_push_token = []
            if expo_push_token not in user_account.expo_push_token:
                user_account.expo_push_token.append(expo_push_token)
                user_account.save()

        return user

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['full_name'] = f"{instance.first_name} {instance.last_name}"
        return ret

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def split_full_name(self, full_name):
        parts = full_name.split()
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

    def get_following(self, obj):
        return [useraccount.user.id for useraccount in obj.useraccount.following.all()]

    def get_followers(self, obj):
        return [useraccount.user.id for useraccount in obj.useraccount.followers.all()]
    
    def get_blocked_users(self, obj):
        return list(obj.useraccount.blocked_users.values_list('id', flat=True))

    def to_representation(self, instance):
        request_user = self.context['request'].user

        # Check if request_user is authenticated and has a useraccount
        if request_user.is_authenticated and hasattr(request_user, 'useraccount'):
            blocked = instance.useraccount.blocked_users.filter(id=request_user.id).exists()
            blocking = request_user.useraccount.blocked_users.filter(id=instance.id).exists()

            if blocked or blocking:
                return {
                    'id': instance.id,
                    'username': instance.username,
                    'profile_picture': instance.useraccount.profile_picture
                }
        else:
            # Handle the case for AnonymousUser
            blocked = False
            blocking = False

        return super().to_representation(instance)


class UserAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    expo_push_token = serializers.JSONField(required=False)
    profile_picture = serializers.URLField(source='useraccount.profile_picture', required=False)

    class Meta:
        model = UserAccount
        fields = (
            "user",
            "interacted_polls",
            "created_at",
            "profile_picture",
            "bio",
            "email",
            "username",
            "expo_push_token",
            "followers",
            "following",
        )


class OptionSerializer(serializers.ModelSerializer):
    votes_count = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = (
            "id",
            "value",
            "votes",
            "votes_count",
            "image_url",
        )
        read_only_fields = ("votes",)

    def get_votes_count(self, obj):
        return obj.votes.count()


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)
    owner_username = serializers.SerializerMethodField()
    owner_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = (
            "id",
            "question",
            "created_at",
            "owner_username",
            "owner_profile_picture",
            "owner",
            "expires",
            "options",
            "image_url",
        )

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(poll=poll, **option_data)
        return poll

    def get_owner_username(self, obj):
        return obj.owner.username

    def get_owner_profile_picture(self, obj):
        if obj.owner and obj.owner.useraccount:
            return obj.owner.useraccount.profile_picture
        return None

    def to_representation(self, instance):
        request_user = self.context['request'].user
        blocked = instance.owner.useraccount.blocked_users.filter(id=request_user.id).exists()
        blocking = request_user.useraccount.blocked_users.filter(id=instance.owner.id).exists()

        # Exclude poll data if the owner is blocked or is blocking the requesting user
        if blocked or blocking:
            return {}  # Return an empty dict or limited data

        return super().to_representation(instance)

class FriendsSerializer(serializers.ModelSerializer):
    profile_picture = serializers.URLField(
        source='useraccount.profile_picture', required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'profile_picture'
        ]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class UserAccountFriendsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    username = serializers.CharField(source='user.username')
    profile_picture = serializers.URLField(source='user.useraccount.profile_picture', required=False)

    class Meta:
        model = UserAccount
        fields = [
            'id',
            'username',
            'profile_picture'
        ]

class FlagPollSerializer(serializers.Serializer):
    post_id = serializers.UUIDField(required=True)
    accused_id = serializers.IntegerField(required=True)
    reporter_id = serializers.IntegerField(required=True)

class BlockUserSerializer(serializers.Serializer):
    accused_id = serializers.IntegerField(required=True)
    reporter_id = serializers.IntegerField(required=True)

from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Poll, UserAccount, Option


class UserSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

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

    class Meta:
        model = User
        fields = [
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
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
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
        return UserFollowSerializer(obj.useraccount.following.all(), many=True).data

    def get_followers(self, obj):
        return UserFollowSerializer(obj.useraccount.followers.all(), many=True).data


class UserAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = (
            "user",
            "interacted_polls",
            "created_at",
            "profile_picture",
            "bio",
            "following",
            "followers",
        )

    def get_following(self, obj):
        return UserFollowSerializer(obj.following.all(), many=True).data

    def get_followers(self, obj):
        return UserFollowSerializer(obj.followers.all(), many=True).data


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email'
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

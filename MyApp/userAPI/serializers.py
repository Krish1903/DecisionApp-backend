from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Poll, UserAccount, Option


class UserSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()

    profile_picture = serializers.URLField(
        source='useraccount.profile_picture', required=False)

    bio = serializers.CharField(
        source='useraccount.bio', required=False)

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        required=True,
        max_length=32,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    full_name = serializers.CharField(
        required=True,
        max_length=64,
    )

    password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True
    )

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    class Meta:
        model = User
        fields = (
            "token",
            "username",
            "password",
            "full_name",
            "email",
            "id",
            "profile_picture",
            "bio",
        )


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
        return UserSerializer(obj.following.all(), many=True).data

    def get_followers(self, obj):
        return UserSerializer(obj.followers.all(), many=True).data


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = (
            "id",
            "question",
            "created_at",
            "owner",
            "expires",
            "options",
            "image_url",
        )


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = (
            "id",
            "value",
            "votes",
            "poll",
            "image_url",
        )

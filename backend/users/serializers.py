import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Followers

from recipes.models import Recipes


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']


class SimpleCustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request is not None and request.user.is_authenticated is True:
            return Followers.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        else:
            return False


class CreateCustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request is None:
            return []

        if request is not None and request.user.is_authenticated is True:
            return Followers.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        else:
            return False

    def get_recipes(self, obj):
        request = self.context.get('request')        

        if request is None:
            return []

        recipes_limit = request.query_params.get('recipes_limit', None)
        recipes = obj.recipes.all()

        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]

        return FollowerRecipesSerializer(
            recipes,
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = "__all__"

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Текущий пароль неверен.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value


class FollowersSerializer(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Followers
        validators = [
            UniqueTogetherValidator(
                queryset=Followers.objects.all(),
                fields=('follower', 'following')
            )
        ]

    def validate(self, data):
        if data.get('follower') == data.get('following'):
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя!"
            )

        return data


class FollowerRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated
)
from rest_framework.views import APIView
from rest_framework.response import Response

from djoser.views import UserViewSet

from .models import Followers
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          FollowersSerializer, SimpleCustomUserSerializer,
                          PasswordSerializer, CreateCustomUserSerializer)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SimpleCustomUserSerializer
        else:
            return CustomUserSerializer

    @action(detail=False,
            methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = SimpleCustomUserSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = PasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        serializer = CreateCustomUserSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def subscribe(self, request, pk=None):
        follower = request.user
        following = get_object_or_404(User, pk=pk)
        followers = Followers.objects.filter(
            follower=follower,
            following=following
        )

        data = {
            'follower': follower.id,
            'following': following.id
        }

        if request.method == 'POST' and followers.exists():
            return Response(
                'Вы уже подписаны на данного пользователя!',
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'GET' or request.method == 'POST':
            serializer = FollowersSerializer(data=data, content=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            followers.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class AvatarViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        if 'avatar' not in request.data:
            return Response(
                {"error": "Поле 'Аватар' обязательно."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = pagination.PageNumberPagination

    def list(self, request):
        print("Запрос на подписки получен")
        limit = request.query_params.get('limit', None)

        followings = User.objects.filter(
            following__follower=request.user
        ).distinct()

        if limit is not None:
            limit = int(limit)
            if limit < followings.count():
                followings = followings[:limit]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(followings, request)

        serializer = CustomUserSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)


class SubscribeViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        follow_user = get_object_or_404(User, id=id)

        if request.user == follow_user:
            return Response(
                {'error': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Followers.objects.filter(
            follower=request.user,
            following=follow_user
        ).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Followers.objects.create(
            follower=request.user,
            following=follow_user
        )

        serializer = CustomUserSerializer(
            follow_user,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        unfollow_user = get_object_or_404(User, id=id)

        subscription = Followers.objects.filter(
            follower=request.user,
            following=unfollow_user
        ).filter()

        if not subscription:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

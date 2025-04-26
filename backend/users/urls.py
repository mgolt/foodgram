from django.urls import path, re_path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, AvatarViewSet,
                    SubscriptionsViewSet, SubscribeViewSet)

router = DefaultRouter()
router.register("users", CustomUserViewSet)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionsViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path("", include(router.urls)),
    path('', include('djoser.urls')),
    re_path("auth/", include("djoser.urls.authtoken")),
    path(
        'users/me/avatar/',
        AvatarViewSet.as_view(),
        name='avatar-update'
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscribeViewSet.as_view(),
        name='subscribe'
    )
]

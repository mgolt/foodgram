from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/avatars',
        null=True,
        blank=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False

    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False
    )

    Followers = models.ManyToManyField(
        'self',
        through='Followers',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Followers(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='followers',
        on_delete=models.CASCADE,
        null=False
    )
    following = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='following',
        on_delete=models.CASCADE,
        null=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('follower', 'following')

from django.db import models
from django.contrib.auth import get_user_model

from tags.models import Tags


User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=254,
        verbose_name='Единица измеренеия'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipes(models.Model):
    tags = models.ManyToManyField(
        Tags,
        through='RecipeTags',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False,
        null=False
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsInRecipe',
        blank=False,
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,
        null=False
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
        blank=True,
        null=True
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False,
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время пригтовления (в минутах)',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientsInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1
    )


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
        related_name='tags',
        blank=False,
        null=False
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )

    class Meta:
        unique_together = ('user', 'recipe')

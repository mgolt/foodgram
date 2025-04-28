import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import (Recipes, Ingredients, RecipeTags, IngredientsInRecipe,
                     Favorite, ShoppingCart)
from tags.models import Tags
from users.serializers import CustomUserSerializer, CustomUserProfileSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=256)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')

        if request is not None and request.user.is_anonymous is False:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')

        if request is not None and request.user.is_anonymous is False:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        else:
            return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags', [])
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient in ingredients_data:
            ingredient_id = ingredient['id']
            ingredient_amount = ingredient['amount']
            IngredientsInRecipe.objects.create(
                ingredient=ingredient_id,
                recipe=recipe,
                amount=ingredient_amount
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags', [])
        RecipeTags.objects.filter(recipe=instance).delete()
        IngredientsInRecipe.objects.filter(recipe=instance).delete()

        for ingredient in ingredients_data:
            ingredient_id = ingredient['id']
            ingredient_amount = ingredient['amount']
            IngredientsInRecipe.objects.create(
                ingredient=ingredient_id,
                recipe=instance,
                amount=ingredient_amount
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.tags.set(tags_data)
        instance.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = RecipeTagsSerializer(
            instance.tags.all(),
            many=True
        ).data
        representation['author'] = CustomUserProfileSerializer(
            instance.author
        ).data
        ingredients = IngredientsInRecipe.objects.filter(recipe=instance)
        representation['ingredients'] = IngredientsInRecipeSerializer(
            ingredients,
            many=True
        ).data

        if instance.image:
            representation['image'] = instance.image.url

        return representation

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        cooking_time = data.get('cooking_time')
        tags = data.get('tags', [])

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': '''Рецепт должен содержать
                 хотя бы один ингредиент!'''}
            )

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'При создании рецепта необходимо указать теги!'}
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': '''Запрос на создание рецепта
                 не должен иметь повторяющихся тегов!'''}
            )

        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    {'ingredients': '''Количество ингредиента
                     должно быть больше нуля!'''}
                )

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': "Ингредиенты не должны повторяться!"}
            )

        if cooking_time <= 0:
            raise serializers.ValidationError(
                {'cooking_time': '''Время приготовления
                 не может быть меньше или равно 0!'''}
            )

        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,                   
            'image': instance.recipe.image.url if instance.recipe.image.url else None,
            'cooking_time': instance.recipe.cooking_time
        }

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном.')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'image': self.context['request'].build_absolute_uri(
                instance.recipe.image.url
            ) if instance.recipe.image else None,
            'cooking_time': instance.recipe.cooking_time
        }

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from hashids import Hashids

from .models import (Recipes, Ingredients, Favorite,
                     ShoppingCart, IngredientsInRecipe)
from .permissions import IsAuthorOrReadOnly
from .serializers import (RecipeSerializer, IngredientsSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)
from .filters import IngredientFilter, RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user:
            serializer.save(author=self.request.user)

    @action(detail=True, methods=['get', 'patch'], url_path='edit')
    def edit(self, request, pk=None):        
        recipe = self.get_object()
        
        if recipe.author != request.user:
            return Response(
                {'detail': 'У вас нет прав для редактирования этого рецепта.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'GET':            
            serializer = self.get_serializer(recipe)
            return Response(serializer.data)

        if request.method == 'PATCH':            
            serializer = self.get_serializer(
                recipe, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = self.generate_short_link(recipe)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    def generate_short_link(self, recipe):
        basse_url = self.request.build_absolute_uri('/')
        hashids = Hashids(salt='your_uniq_salt', min_length=6)
        hashid = hashids.encode(recipe.id)
        return f'{basse_url}s/{hashid}'


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class FavoriteViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipes, id=recipe_id)

        if Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {'error': 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }

        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipes, id=recipe_id)

        if Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            Favorite.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ShoppingCartViewSet(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipes, id=recipe_id)

        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe.id
        ).exists():
            return Response(
                {'error': 'Рецепт уже добавлен в корзину!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }

        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipes, id=recipe_id)

        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe_id
        ).exists():
            ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DownloadShoppingCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        shopping_cart_items = ShoppingCart.objects.filter(user=request.user)
        recipes = (item.recipe for item in shopping_cart_items)

        ingredients = {}

        for recipe in recipes:
            ingredients_in_recipe = IngredientsInRecipe.objects.filter(
                recipe=recipe
            )

            for ingredient_in_recipe in ingredients_in_recipe:
                name = ingredient_in_recipe.ingredient.name
                amount = ingredient_in_recipe.amount

                if name in ingredients:
                    ingredients[name] += amount
                else:
                    ingredients[name] = amount

        file_content = 'Список покупок:\n\n'

        for name, amount in ingredients.items():
            file_content += f'{name}: {amount}\n'

        response = HttpResponse(
            file_content,
            content_type='text/plain'
        )

        response['Content-Disposition'] = 'attachment; filename="shopcart.txt"'

        return response

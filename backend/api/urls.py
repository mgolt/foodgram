from django.urls import path, include

from rest_framework import routers

from tags.views import TagsViewSet
from recipes.views import (RecipeViewSet, IngredientsViewSet,
                           FavoriteViewSet, ShoppingCartViewSet,
                           DownloadShoppingCartView)


router = routers.DefaultRouter()
router.register(r'tags', TagsViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(),
        name='favorite'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download_shopping_cart'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view(),
        name='shopping_cart'
    ),
    path('', include(router.urls))
]

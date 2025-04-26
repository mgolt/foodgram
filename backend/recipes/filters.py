import django_filters as filters
from .models import Ingredients, Recipes
from tags.models import Tags


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')    
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_filter'
    )
    is_favorited = filters.NumberFilter(
        method='is_favorited_filter'
    )

    class Meta:
        model = Recipes
        fields = (
            'author',
            'is_in_shopping_cart',
            'tags',
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if value == 1:
            return queryset.filter(shopping_cart__user=user)
        else:
            return queryset.exclude(shopping_cart__user=user)

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if value == 1:
            return queryset.filter(favorite__user=user)
        else:
            return queryset.exclude(favorite__user=user)

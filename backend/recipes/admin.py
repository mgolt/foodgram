from django.contrib import admin

from .models import Recipes, Ingredients


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_author_full_name', 'get_favorite_count')
    list_filter = ('author', 'tags')
    search_fields = ('name', 'tags__name', 'author__username')

    def get_author_full_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"
    get_author_full_name.short_description = 'Автор'

    def get_favorite_count(self, obj):
        return obj.favorite.count()
    get_favorite_count.short_description = 'Добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Recipes, RecipeAdmin)
admin.site.register(Ingredients, IngredientAdmin)

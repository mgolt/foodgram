from django.contrib import admin

from .models import Tags


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Tags, TagsAdmin)

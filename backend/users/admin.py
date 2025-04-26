from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Followers

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar',)}),
)
UserAdmin.search_fields += ('email',)


class FollowersAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')
    list_filter = ('follower', 'following')


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Followers, FollowersAdmin)

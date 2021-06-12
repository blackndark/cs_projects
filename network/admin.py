from django.contrib import admin

from . models import User, Post, Follower, Liked

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "password")


class PostAdmin(admin.ModelAdmin):
    list_display = ("creator", "content", "timestamp", "likes")


class FollowerAdmin(admin.ModelAdmin):
    list_display = ("creator", "follower")


class LikedAdmin(admin.ModelAdmin):
    list_display = ("post", "follower")


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Follower, FollowerAdmin)
admin.site.register(Liked, LikedAdmin)

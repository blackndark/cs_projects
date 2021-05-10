from django.contrib import admin

from .models import User, Listings, Watchlist, Comment, Bid, Wonauction

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "password", "age", "gender")

class ListingsAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "sarting_bid", "image", "category", "active", "maximum_bid")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "listings")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "comment")

class BidAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "bid")

class WonauctionAdmin(admin.ModelAdmin):
    list_display = ("user", "listing")


admin.site.register(User, UserAdmin)
admin.site.register(Listings, ListingsAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Wonauction, WonauctionAdmin)
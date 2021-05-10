from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_listing, name="new_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("wonauctions", views.won_auctions, name="won_auctions"),
    path("categories", views.categories, name="categories"),
    path("bid/<str:title>", views.bid, name="bid"),
    path("bid/<str:title>/error", views.bid_error, name="bid_error"),
    path("comment/<str:title>", views.comment, name="comment"),
    path("categories/<str:category>", views.category_name, name="category_name"),
    path("add_remove_watchlist/<str:title>", views.add_remove_watchlist, name="add_remove_watchlist"),
    path("close_auction/<str:title>", views.close_auction, name="close_auction"),
    path("listing/<str:title>", views.listing, name="listing")
]

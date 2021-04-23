from django.urls import path

from . import views

app_name = "wiki"

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search_func, name="search_func"),
    path("new", views.new_page, name="new_page"), 
    path("random", views.random_page, name="random_page"),
    path("edit/<str:title>", views.edit_page, name="edit_page"),
    path("<str:title>", views.entry_page, name="entry_page")
]


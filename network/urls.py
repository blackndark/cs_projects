
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("new", views.new_post, name="new_post"),
    #path("posts", views.load_allposts, name="load_allposts"),
    #path("posts/<str:username>", views.load_profile, name="load_profile"),
    path("follow_button/<str:username>",
         views.follow_button, name="follow_button"),
    path("profile/<str:username>", views.profile_followers,
         name="profile_followers"),

    # Fetching follow or unfollow result instantly without refreshing page
    path("follow_unfollow/<str:username>",
         views.follow_unfollow, name="follow_unfollow"),

    # Fetching post likes instantly without refreshing page
    path("postlikes/<int:post_id>", views.postlikes, name="postlikes"),

    path("follow", views.follow, name="follow"),
    path("following_posts", views.following_posts, name="following_posts"),
    path("save/<int:post_id>", views.save, name="save"),
    path("like", views.like, name="like"),

    # Fetching like button states instantly without refreshing page
    path("like_button/<int:post_id>", views.like_button, name="like_button")
]

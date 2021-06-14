import json
from django.contrib.auth import authenticate, login, logout
from django.core import paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post, Follower, Liked


# All Pages
def index(request):
    # Show all created posts
    all_posts = Post.objects.all()

    # Return posts in reverse chronological order
    all_posts = all_posts.order_by("-timestamp").all()

    # Using Paginator class to show 10 posts per page
    paginator = Paginator(all_posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, "network/index.html", {
        'posts': posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required(login_url="/login")
def new_post(request):

    # Sending a new post must be a POST request
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check if there is any content
    data = json.loads(request.body)
    post_content = data.get("content")
    if post_content == "":
        return JsonResponse({"error": "Post content required"}, status=400)

    # Create the post
    Post.objects.create(
        creator=request.user,
        content=post_content
    )

    return JsonResponse({"message": "New post succesfully submitted."}, status=201)


# Check to see if the creator follower duo is already in the table. So that we'll decide on the state of the Follow/Unfollow button.
@login_required(login_url="/login")
def follow_button(request, username):

    # Select the user with the given username
    user = User.objects.get(username=username)

    # Check if there is such a creator, follower set
    if (Follower.objects.filter(creator=user, follower=request.user)):
        return JsonResponse({"followed": "Creator already followed"}, status=201)
    else:
        return JsonResponse({"not followed": "Creator is not followed yet"}, status=201)


# Pull all posts and add follower & following numbers to the profile section of the given user profile.
def profile_followers(request, username):

    # Find the user with given username
    user = User.objects.get(username=username)

    # Filter the followers of the given user and count followers
    user_followers = Follower.objects.filter(creator=user)
    followers_number = user_followers.count()

    # Filter the followings of the given user and count followings
    user_following = Follower.objects.filter(follower=user)
    following_number = user_following.count()

    # All posts created by the given user
    user_posts = Post.objects.filter(creator=user)

    # Return posts in reverse chronological order
    user_posts = user_posts.order_by("-timestamp").all()

    # Using Paginator class to show 10 posts per page
    paginator = Paginator(user_posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, "network/profile.html", {
        "followers": followers_number,
        "following": following_number,
        "posts": posts,
        "profile_user": username
    })


# Run follow function to create a new set of creator and follower
@csrf_exempt
@login_required(login_url="/login")
def follow(request):

    # Make sure the request is a POST request
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    # Make sure there is content in the received data.(both creator and follower)
    data = json.loads(request.body)
    creator = data.get("creator")
    follower = data.get("follower")
    if not (creator or follower):
        return JsonResponse({"error": "Creator and Follower required"}, status=400)

    # Get User instances
    creator = User.objects.get(username=creator)
    follower = User.objects.get(username=follower)

    # Create or delete new creator and follower (Follow or Unfollow toggle)
    if not (Follower.objects.filter(creator=creator, follower=follower)):
        Follower.objects.create(creator=creator, follower=follower)
        return JsonResponse({"message": "New creator follower set successfully created"}, status=201)
    else:
        Follower.objects.filter(creator=creator, follower=follower).delete()
        return JsonResponse({"unfollowed": "New creator follower set successfully deleted"}, status=201)


# Load only posts from the people that the logged in user follows.
@csrf_exempt
@login_required(login_url="/login")
def following_posts(request):

    # Select the logged in user
    user = User.objects.get(username=request.user)

    # Select all the creatores that the logged in user is following
    followed_creators = Follower.objects.filter(follower=user)

    # And put them in a list
    creators = []
    for followed_creator in followed_creators:
        creators.append(followed_creator.creator)

    # Pull all the posts of the creators by using their user instances
    creator_posts = []
    for creator in creators:
        posts = Post.objects.filter(creator=creator)
        for post in posts:
            creator_posts.append(post)

    # Although it's probably better to let the SQL server do the ordering, we had to order here due to having a list.
    creator_posts.reverse()

    # Using Paginator class to show 10 posts per page
    paginator = Paginator(creator_posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, "network/following.html", {
        "posts": posts
    })


# Sending JsonResponse to fetch instantly Follow or Unfollow result without refreshing page
def follow_unfollow(request, username):

    # Find the user with given username
    user = User.objects.get(username=username)

    # Filter the followers of the given user and count followers
    user_followers = Follower.objects.filter(creator=user)
    followers_number = user_followers.count()

    # Filter the followings of the given user and count followings
    user_following = Follower.objects.filter(follower=user)
    following_number = user_following.count()

    return JsonResponse({
        "followers": followers_number,
        "following": following_number
    })


# Save edited post
@csrf_exempt
@login_required(login_url="/login")
def save(request, post_id):

    post = Post.objects.get(pk=post_id)

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required to save the change"})

    data = json.loads(request.body)
    if data["content"] == "":
        return JsonResponse({"error": "There is no content to save"})
    else:
        post.content = data["content"]
        post.save()
        return JsonResponse({"message": "Post has been successfully saved"})


# like any given post by creating a post and follower set.
@csrf_exempt
@login_required(login_url="/login")
def like(request):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required for like functionality"})

    data = json.loads(request.body)
    post_id = data.get("post_id")
    follower_username = data.get("follower")

    if not (post_id or follower_username):
        return JsonResponse({"error": "post_id and follower required"})

    follower_user = User.objects.get(username=follower_username)
    post = Post.objects.get(pk=post_id)

    if not (Liked.objects.filter(post=post, follower=follower_user)):
        Liked.objects.create(post=post, follower=follower_user)
        post.likes += 1
        post.save()
        return JsonResponse({"liked": "Post and Follower set has been created(Post liked)"})
    else:
        Liked.objects.filter(post=post, follower=follower_user).delete()
        post.likes -= 1
        post.save()
        return JsonResponse({"disliked": "Post and Follower set has been deleted(Post disliked)"})


# Sending JsonResponse to fetch instantly like count without refreshing page
def postlikes(request, post_id):

    post = Post.objects.get(pk=post_id)

    return JsonResponse({
        "post_likes": post.likes
    })


# Sending JsonResponse to fetch instantly like buttons states without refreshing page
def like_button(request, post_id):

    post = Post.objects.get(pk=post_id)

    if (Liked.objects.filter(post=post, follower=request.user)):
        return JsonResponse({"liked": "Logged in user has already liked the post"})
    else:
        return JsonResponse({"not liked": "Logged in user has NOT liked the post"})

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import User, Listings, Watchlist, Comment, Bid, Wonauction


# Create a ModelForm for listings
class ListingForm(forms.ModelForm):
    # The name of the model to use
    class Meta:
        model = Listings
        fields = ('title', 'description', 'sarting_bid', 'image', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs = {
            'class': 'form-control'}
        self.fields['description'].widget.attrs = {
            'class': 'form-control'}
        self.fields['sarting_bid'].widget.attrs = {
            'class': 'form-control'}
        self.fields['image'].widget.attrs = {
            'class': 'form-control'}
        self.fields['category'].widget.attrs = {
            'class': 'form-control'}

# Create a ModelForm for comments
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)
    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs = {
            'class': 'form-control'}

# Create a ModelForm for bids
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ('bid',)

    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        self.fields['bid'].widget.attrs = {
            'class': 'form-control mx-sm-3'}


def index(request):
    all_listings = Listings.objects.filter(active=True)
    for listing in all_listings:
        highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))
        max_bid = highest_bid['bid__max']
        listing.maximum_bid = max_bid
        listing.save()
    return render(request, "auctions/index.html", {
        "all_listings": all_listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["sarting_bid"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            Listings.objects.create(user=request.user, title=title, description=description, sarting_bid=starting_bid, image=image, category=category)
            listing = Listings.objects.get(title=title)
            return HttpResponseRedirect(reverse("listing", args=(listing.title,)))
    else:
        return render(request, "auctions/new_listing.html", {
            "form": ListingForm()
        })    


# show a listing page
def listing(request, title):
    # Select, in other words instantiate, the listing with the given title.
    listing = Listings.objects.get(title=title)
    # Show if the listing is in the watchlist of the user. 2 conditions as anonymous user does not return value from request.user
    if request.user.is_authenticated:
        watchlist_item = Watchlist.objects.filter(user=request.user, listings=listing).first()
    else:
        watchlist_item = Watchlist.objects.filter(listings=listing).first()
    # Check if the current user is the current highest bidder
    highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid')) # Creates a dict: highest_bid = {'bid__max' : ....}
    current_user_highest_bidder = False
    if highest_bid['bid__max']:
        bid = Bid.objects.filter(bid=highest_bid['bid__max'], listing=listing).first()  # get() doesn't work here. why???
        if bid.user == request.user:
            current_user_highest_bidder = True
    # Check if the current user is the creater of the listing
    current_user_creator = False
    if request.user == listing.user:
        current_user_creator = True
    # Calculate total bid count
    bid_count = Bid.objects.filter(listing=listing).count()
    # Show user comments
    user_comments = Comment.objects.filter(listing=listing)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist_items": watchlist_item,
        "max_bid": highest_bid['bid__max'],
        "bid_count": bid_count,
        "current_user_highest_bidder": current_user_highest_bidder,
        "bid_form": BidForm(),
        "current_user_creator": current_user_creator,
        "comment_form": CommentForm(),
        "user_comments": user_comments
    })


# Show watchlist
@login_required(login_url='/login')
def watchlist(request):
    user = request.user
    watchlist_items = Watchlist.objects.filter(user=user)
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items,
        "watchlist_count": watchlist_items.count()
    })


# Add or Remove a listing to a watchlist
@login_required(login_url='/login')
def add_remove_watchlist(request, title):
    user = request.user
    listing = Listings.objects.get(title=title)
    watchlist_item = Watchlist.objects.filter(user=user, listings=listing).first()
    if not watchlist_item:
        Watchlist.objects.create(user=user, listings=listing)
        return HttpResponseRedirect(reverse("listing", args=(listing.title,)))
    else:
        watchlist_item.delete()
        return HttpResponseRedirect(reverse("listing", args=(listing.title,)))


# Show all the categories of listings
def categories(request):
    listings = Listings.objects.all()
    category_list = []
    for listing in listings:
        if listing.category not in category_list:
            category_list.append(listing.category)
    return render(request, "auctions/categories.html", {
        "categories": category_list
    })


# Show the listings under a selected category
def category_name(request, category):
    listing = Listings.objects.filter(category=category)
    return render(request, "auctions/category_name.html", {
        "category_listings": listing,
        "category": category
    })


@login_required(login_url='/login')
def comment(request, title):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            listing = Listings.objects.get(title=title)
            Comment.objects.create(user=request.user, listing=listing, comment=comment)
            return HttpResponseRedirect(reverse("listing", args=(listing.title,)))


@login_required(login_url='/login')
def bid(request, title):
    if request.method =="POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            listing = Listings.objects.get(title=title)
            if bid >= listing.sarting_bid:
                highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))
                if highest_bid['bid__max']:
                    if bid > highest_bid['bid__max']:
                        Bid.objects.create(user=request.user, listing=listing, bid=bid)
                        return HttpResponseRedirect(reverse("listing", args=(listing.title,)))
                    else:
                        return HttpResponseRedirect(reverse("bid_error", args=(listing.title,)))
                else:
                    Bid.objects.create(user=request.user, listing=listing, bid=bid)
                    return HttpResponseRedirect(reverse("listing", args=(listing.title,)))
            else:
                return HttpResponseRedirect(reverse("bid_error", args=(listing.title,)))


@login_required(login_url='/login')
def bid_error(request, title):
    listing = Listings.objects.get(title=title)
    if request.user.is_authenticated:
        watchlist_item = Watchlist.objects.filter(user=request.user, listings=listing).first()
    else:
        watchlist_item = Watchlist.objects.filter(listings=listing).first()
    highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid')) # Creates a dict: highest_bid = {'bid__max' : ....}
    user_comments = Comment.objects.filter(listing=listing)
    bid_count = Bid.objects.filter(listing=listing).count()
    # Check if the current user is the current highest bidder
    current_user_highest_bidder = False
    if highest_bid['bid__max']:
        bid = Bid.objects.filter(bid=highest_bid['bid__max']).first()  # get() doesn't work here. why???
        if bid.user == request.user:
            current_user_highest_bidder = True
    # Check if the current user is the creater of the listing
    current_user_creator = False
    if request.user == listing.user:
        current_user_creator = True
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist_items": watchlist_item,
        "bid_error": True,
        "max_bid": highest_bid['bid__max'],
        "bid_count": bid_count,
        "current_user_highest_bidder": current_user_highest_bidder,
        "bid_form": BidForm(),
        "current_user_creator": current_user_creator,
        "comment_form": CommentForm(),
        "user_comments": user_comments
    })


# Show all the auctions that the logged-in user won.
@login_required(login_url='/login')
def won_auctions(request):
    won_auctions = Wonauction.objects.filter(user=request.user)
    return render(request, "auctions/won_auctions.html", {
        "won_auctions": won_auctions
    }) 

# Give the listing creater ability to close the listing and automatically add the listing to winner's "Won Auctions" section.
@login_required(login_url='/login')
def close_auction(request, title):
    listing = Listings.objects.get(title=title)
    if request.user == listing.user:
        # Deactivate listing
        listing.active = False
        listing.save()
        # Add the listing to the "Won Auctions" section for the winner
        highest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))
        if highest_bid['bid__max']:
            bid = Bid.objects.filter(bid=highest_bid['bid__max']).first()
            Wonauction.objects.create(listing=listing, user=bid.user)
            return HttpResponseRedirect(reverse("listing", args=(listing.title,)))


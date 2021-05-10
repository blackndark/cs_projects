from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    age = models.CharField(max_length=2, null=True, blank=True)

    Male = "M"
    Female = "F"
    GENDER_CHOICES = [
        (Male, "Male"),
        (Female, "Female")
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=Male)


class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)     
    sarting_bid = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    image = models.URLField(null=True, blank=True)       
    
    COLLECTIBLES = "Collectibles"
    FASHION = "Fashion"
    SPORTING_GOODS = "Sporting goods"
    ELECTRONICS = "Electronics"
    HOME_AND_GARDEN = "Home and Garden"
    TOYS_AND_HOBBIES = "Toys and Hobbies"
    ENTERTAINMENT = "Entertainment"
    MOTORS = "Motors"
    OTHER = "Other"

    CATEGORIES = [
        (COLLECTIBLES, "Collectibles"),
        (FASHION, "Fashion"),
        (SPORTING_GOODS, "Sporting goods"),
        (ELECTRONICS, "Electronics"),
        (HOME_AND_GARDEN, "Home and Garden"),
        (TOYS_AND_HOBBIES, "Toys and Hobbies"),
        (ENTERTAINMENT, "Entertainment"),
        (MOTORS, "Motors"),
        (OTHER, "Other")
    ]
    category = models.CharField(max_length=64, choices=CATEGORIES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank="False", null=True)
    active = models.BooleanField(default=True)
    maximum_bid = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.title} {self.sarting_bid} {self.category}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank="False")
    listings = models.ForeignKey(Listings, on_delete=models.CASCADE, blank="True", null=True)
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank="False")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank="False", null=True)
    comment = models.TextField(max_length=1000)


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank="False")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank="False", null=True)
    bid = models.FloatField()

class Wonauction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank="False")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank="False", null=True)


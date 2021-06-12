from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import DateField, DateTimeField


class User(AbstractUser):
    pass


class Post(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, null=True, related_name="posts_created")
    content = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0, blank=True, null=True)

    def serialize(self):
        return {
            "id": self.id,
            "creator": self.creator.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes
        }


class Follower(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=True, related_name="creator")
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=True, related_name="follower")

    def serialize(self):
        return {
            "id": self.id,
            "creator": self.creator.username,
            "follower": self.follower.username
        }


class Liked(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, blank=False, null=True)
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=True)

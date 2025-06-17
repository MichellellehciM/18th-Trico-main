from django.db import models
from django.contrib.auth.models import User
from utils.mixins import WebPImageModelMixin

# Create your models here.


class Profile(WebPImageModelMixin,models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    bio = models.TextField(max_length=200, null=True)
    location = models.CharField(max_length=50, null=True)
    is_client = models.BooleanField(default=True, null=True)
    is_freelancer = models.BooleanField(default=False, null=True)
    freelancer_verified = models.BooleanField(default=False, null=True)


    def __str__(self):
        return f"{self.user.username}'s Profile"

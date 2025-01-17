from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from utils.mixins import WebPImageModelMixin
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager


class Service(WebPImageModelMixin, models.Model):
    freelancer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="services",
        null=True,
    )
    category = models.ManyToManyField(
        Category,
        related_name="services",
    )
    title = models.CharField(max_length=100)
    description = CKEditor5Field(config_name="extends")
    photo = models.ImageField(upload_to="service_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 新增一般方案
    standard_title = models.CharField(max_length=100)
    standard_description = models.TextField()
    standard_price = models.PositiveIntegerField()
    standard_delivery_time = models.PositiveIntegerField(null=True, blank=True)

    # 新增專業方案
    premium_title = models.CharField(max_length=100, blank=True, null=True)
    premium_description = models.TextField(blank=True, null=True)
    premium_price = models.PositiveIntegerField(blank=True, null=True)
    premium_delivery_time = models.PositiveIntegerField(blank=True, null=True)

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
        default=None,
        help_text="Client rating for the service (e.g., 4.5 stars)",
    )

    tags = TaggableManager()    

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} likes {self.service.title}"
    

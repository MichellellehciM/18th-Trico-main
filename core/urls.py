from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from common.views import custom_404
from django.conf.urls.static import static
from .views import vue404_page
from django.urls import re_path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("users/", include("users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("order/", include("order.urls")),
    path("services/", include("services.urls")),
    path("categories/", include("categories.urls")),
    path("comments/", include("comments.urls")),
    path("api/", include("common.urls")),
    path("", include("ckeditor.urls")), 
    path("contact/", include("contact.urls")),
    path("search/", include("search.urls")),
    path("notification/", include("notification.urls")),
    path("chat/", include("rtchat.urls")),

]

handler404 = custom_404

urlpatterns += [
    re_path(r"^(?!admin|users|accounts|order|services|categories|comments|api|chat|/).*", vue404_page),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





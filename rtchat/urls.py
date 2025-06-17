from django.urls import path, re_path
from .views import *
from . import views
# app_name = "chat"  

urlpatterns = [
    path("chat/unread-chatroom-status/", views.unread_chatroom_status, name="unread_chatroom_status"),

    path("", chat_view, name="home"),
    path("chat/room/<chatroom_name>/", chat_view, name="chatroom"),
    re_path(r"^chat/(?P<username>[\w.@+-]+)/$", get_or_create_chatroom, name="start-chat"),
    path('unread-message-count/', views.unread_message_count, name='unread_message_count'),
    path("message-dot/", views.unread_message_badge, name="unread_message_badge"),



]

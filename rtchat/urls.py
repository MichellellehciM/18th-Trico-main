from django.urls import path, re_path
from .views import *

urlpatterns = [
    path("", chat_view, name="home"),
    path("chat/room/<chatroom_name>/", chat_view, name="chatroom"),
    re_path(r"^chat/(?P<username>[\w.@+-]+)/$", get_or_create_chatroom, name="start-chat"),
]

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import ChatGroup
from .forms import ChatmessageCreateForm
from django.contrib.auth.models import User
from urllib.parse import unquote


@login_required
def chat_view(request, chatroom_name="public-chat"):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all().select_related("author")[:30]
    form = ChatmessageCreateForm()
    
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404("您無法訪問此聊天群組")
        other_user = chat_group.members.exclude(id=request.user.id).first()
        if not other_user:
            raise Http404("聊天對象並不存在。")

    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                "message": message,
                "user": request.user,
            }
            return render(request, "rtchat/partials/chat_message_p.html", context)
    
    context = {
        "chat_messages": chat_messages,
        "form": form,
        "other_user": other_user,
        "chatroom_name": chatroom_name,
        "chat_group": chat_group,
    }
    return render(request, "rtchat/chat.html", context)


@login_required
def get_or_create_chatroom(request, username):
    username = unquote(username)
    other_user = get_object_or_404(User, username=username)

    if request.user.username == username:
        return redirect("users:information")
    
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    for chatroom in my_chatrooms:
        if other_user in chatroom.members.all():
            return redirect("chatroom", chatroom.group_name)

    # 若沒有現成聊天室，創建一個
    chatroom = ChatGroup.objects.create(is_private=True)
    chatroom.members.add(other_user, request.user)
    return redirect("chatroom", chatroom.group_name)

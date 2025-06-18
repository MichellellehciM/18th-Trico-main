from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import ChatGroup
from .forms import ChatmessageCreateForm
from django.contrib.auth.models import User
from urllib.parse import unquote
from django.http import JsonResponse
from .models import GroupMessage, MessageReadStatus




from .models import MessageReadStatus

@login_required
def chat_view(request, chatroom_name="public-chat"):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()
    
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404("您無法訪問此聊天群組")
        other_user = chat_group.members.exclude(id=request.user.id).first()
        if not other_user:
            raise Http404("聊天對象並不存在。")

    # 將未讀訊息標記為已讀
    unread_messages = chat_group.chat_messages.exclude(
        read_statuses__user=request.user
    )
    MessageReadStatus.objects.bulk_create([
        MessageReadStatus(message=msg, user=request.user, read=True)
        for msg in unread_messages
    ], ignore_conflicts=True)

    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid:
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                "message" : message,
                "user" : request.user,
            }
            return render(request, "rtchat/partials/chat_message_p.html", context)

    context = {
        "chat_messages" : chat_messages, 
        "form" : form,
        "other_user" : other_user,
        "chatroom_name" : chatroom_name,
        "chat_group" : chat_group
    }
    
    return render(request, "rtchat/chat.html", context)





@login_required
def get_or_create_chatroom(request, username):
    username = unquote(username)
    other_user = get_object_or_404(User, username=username)

    if request.user.username == username:
        return redirect("users:information")

    # 查詢是否已存在由雙方組成的 private chatroom
    chatroom = (
        ChatGroup.objects
        .filter(is_private=True, members=request.user)
        .filter(members=other_user)
        .first()
    )

    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(request.user, other_user)

    return redirect("chatroom", chatroom.group_name)








def unread_message_count(request):
    if request.user.is_authenticated:
        unread = GroupMessage.objects.filter(
            group__members=request.user
        ).exclude(
            read_statuses__user=request.user
        ).exclude(
            author=request.user
        ).count()
        return JsonResponse({'unread_count': unread})
    return JsonResponse({'unread_count': 0})




def unread_message_badge(request):
    if request.user.is_authenticated:
        unread_count = GroupMessage.objects.filter(
            group__members=request.user
        ).exclude(
            read_statuses__user=request.user
        ).exclude(
            author=request.user
        ).count()
    else:
        unread_count = 0
    return render(request, "rtchat/message_dot.html", {"count": unread_count})


@login_required
def unread_chatroom_status(request):
    user = request.user
    chatgroups = ChatGroup.objects.filter(members=user, is_private=True).distinct()

    unread_groups = (
        GroupMessage.objects
        .filter(group__in=chatgroups)
        .exclude(read_statuses__user=user)
        .exclude(author=user)
        .values_list("group_id", flat=True)
        .distinct()
    )

    result = []
    for group in chatgroups:
        other_user = group.members.exclude(id=user.id).first()
        result.append({
            "group_name": group.group_name,
            "username": other_user.username if other_user else "未知",
            "has_unread": group.id in unread_groups
        })
    
    return JsonResponse({"data": result})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import ChatGroup
from .forms import ChatmessageCreateForm
import uuid  
from django.contrib.auth.models import User


@login_required
def chat_view(request, chatroom_name):
    # 查找對應的聊天房間
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    # 驗證聊天室是否為私人房間，以及成員是否只有兩人
    if not chat_group.is_private or chat_group.members.count() != 2:
        raise Http404("聊天室不存在或無法訪問")

    # 確認當前用戶是否為該聊天室成員
    if request.user not in chat_group.members.all():
        raise Http404("您無法訪問此聊天室")

    # 找出聊天對象
    other_user = None
    for member in chat_group.members.all():
        if member != request.user:
            other_user = member
            break

    # 取得最近的聊天消息
    chat_messages = chat_group.chat_messages.all()[:30]

    # 聊天訊息表單
    form = ChatmessageCreateForm()

    

    # HTMX 請求處理
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
    }
    return render(request, "rtchat/chat.html", context)





@login_required
def get_or_create_chatroom(request, username):
    # 禁止用戶與自己聊天
    if request.user.username == username:
        return redirect('services:service_detail')

    # 根據 username 獲取其他用戶
    other_user = get_object_or_404(User, username=username)

    # 查找是否已經有私聊房間
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    chatroom = None
    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                break
        else:
            # 如果沒有找到現有的房間，創建新的
            chatroom_name = str(uuid.uuid4())  # 生成唯一房間名稱
            chatroom = ChatGroup.objects.create(group_name=chatroom_name, is_private=True)
            chatroom.members.add(request.user, other_user)
    else:
        # 如果用戶沒有任何房間，創建新的
        chatroom_name = str(uuid.uuid4())
        chatroom = ChatGroup.objects.create(group_name=chatroom_name, is_private=True)
        chatroom.members.add(request.user, other_user)

    # 重定向到聊天房間
    return redirect('chatroom', chatroom_name=chatroom.group_name)
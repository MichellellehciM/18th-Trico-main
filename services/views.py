from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Service, Like
from .forms import ServiceForm
from .models import Category
from comments.models import Comment
from comments.forms import CommentForm
from django.db import models
import json
from django.http import JsonResponse
from notification.utils import send_notification
from notification.models import Notification
from .permissions import has_permission


def has_permission(request, id):
    return request.user.id == id


@login_required
def freelancer_dashboard(request, id):

    if not has_permission(request, id):
        return redirect("services:error_page")

    freelancer = request.user

    services = (
        Service.objects.prefetch_related("category")
        .filter(freelancer_user=freelancer)
        .order_by("-created_at")
    )

    return render(
        request,
        "services/freelancer_dashboard.html",
        {
            "freelancer": freelancer,
            "services": services,
        },
    )


@login_required
def create_service(request, id):
    if not has_permission(request, id):
        return redirect("services:error_page")

    categories = Category.objects.all()

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.freelancer_user = request.user
            service.save()

            selected_categories = request.POST.getlist("category")
            service.category.set(selected_categories)

            tags_input = request.POST.get("tags", "")
            if tags_input:
                service.tags.set(
                    [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                )
            else:
                service.tags.clear()

            form.save_m2m()
            return redirect("services:freelancer_dashboard", id=id)
    else:
        form = ServiceForm()

    return render(
        request,
        "services/create_service.html",
        {
            "form": form,
            "categories": categories,
            "show_loading": True,  # 傳遞顯示 loading 的標記到模板
        },
    )


@login_required
def edit_service(request, id, service_id):
    if not has_permission(request, id):
        return redirect("services:error_page")

    service = get_object_or_404(Service, id=service_id, freelancer_user=request.user)
    categories = Category.objects.all()
    tags = list(service.tags.names())

    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            selected_categories = request.POST.getlist("category")
            service.category.set(selected_categories)

            tags_input = request.POST.get("tags", "")
            if tags_input:
                service.tags.set(
                    [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                )
            else:
                service.tags.clear()

            return redirect("services:freelancer_dashboard", id=id)
    else:
        form = ServiceForm(instance=service)

    return render(
        request,
        "services/edit_service.html",
        {
            "form": form,
            "categories": categories,
            "show_loading": True,  # 傳遞顯示 loading 的標記到模板
            "tags": tags,
        },
    )


@login_required
def delete_service(request, id, service_id):
    if not has_permission(request, id):
        return redirect("services:error_page")

    service = get_object_or_404(Service, id=service_id, freelancer_user=request.user)

    if request.method == "POST":
        service.delete()
        return redirect("services:freelancer_dashboard", id=id)

    return render(
        request, "services/delete_service.html", {"service": service, "id": id}
    )


def error_page(request):
    return render(
        request,
        "services/error_page.html",
        {"message": "You do not have permission to view this page."},
    )


@login_required
def service_detail(request, id, service_id):

    if not request.user.is_authenticated:
        return redirect("users:login")  # 重導向到登入頁面

    service = get_object_or_404(Service, id=service_id)

    tags = service.tags.all()

    print("服務ID:", service_id)
    print("標籤列表:", list(tags))

    comments = Comment.objects.filter(service=service, is_deleted=False).order_by(
        "-created_at"
    )

    total_reviews = comments.count()
    average_rating = comments.aggregate(models.Avg("rating"))["rating__avg"]
    grouped_ratings = comments.values("rating").annotate(count=models.Count("rating"))
    stars_count = {i: 0 for i in range(1, 6)}

    for group in grouped_ratings:
        stars_count[group["rating"]] = group["count"]

    try:
        comment = Comment.objects.get(service=service, user=request.user)
    except Comment.DoesNotExist:
        comment = None

    form = CommentForm(request.POST or None, instance=comment)
    is_liked = Like.objects.filter(user=request.user, service=service).exists()

    # 獲取未讀通知
    unread_notifications = Notification.objects.filter(
        recipient=request.user, unread=True
    )

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.service = service
            comment.rating = request.POST.get("rating")
            comment.is_deleted = False
            comment.deleted_at = None
            comment.save()

            # 發送通知
            if service.freelancer_user != request.user:  # 不通知自己
                send_notification(
                    actor=request.user,
                    recipient=service.freelancer_user,
                    verb="評論了您的服務",
                    description=f"{request.user.username} 評論了您的服務 {service.title}",
                    target_service=service,
                )
            return redirect(
                "services:service_detail", id=request.user.id, service_id=service_id
            )

    if comment and comment.is_deleted:
        comment = None
        form = CommentForm()

    return render(
        request,
        "services/service_detail.html",
        {
            "service": service,
            "comments": comments,
            "comment": comment,
            "form": form,
            "stars_count": stars_count,
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "is_liked": is_liked,
            "unread_notifications": unread_notifications,  # 傳遞未讀通知到模板
            "tags": tags,
        },
    )


def toggle_like(request, service_id):
    # 檢查用戶是否已登入
    if not request.user.is_authenticated:
        return JsonResponse({"login_required": True})

    # 確保服務存在
    service = get_object_or_404(Service, id=service_id)

    # 檢查用戶是否已經點過愛心
    existing_like = Like.objects.filter(user=request.user, service=service).first()

    if existing_like:
        # 如果已經點過愛心，則取消
        existing_like.delete()
        is_liked = False
    else:
        # 未點過愛心，則新增
        Like.objects.create(user=request.user, service=service)
        is_liked = True

        # 發送通知
        if service.freelancer_user != request.user:  # 不通知自己
            send_notification(
                actor=request.user,
                recipient=service.freelancer_user,
                verb="點讚了您的服務",
                description=f"{request.user.username} 點讚了您的服務 {service.title}",
                target_service=service,
            )

    return JsonResponse({"is_liked": is_liked})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from comments.models import Comment
from services.models import Like
from order.models import Order
from django.http import JsonResponse
from notification.models import Notification
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.messages.storage.fallback import FallbackStorage


def register(request):
    if request.user.is_authenticated:
        return redirect("pages:home")

    if request.POST:
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "兩次密碼輸入不一致！")
            return redirect("users:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, f"使用者 {username} 已被註冊！")
            return redirect("users:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, f"信箱 {email} 已被註冊！")
            return redirect("users:register")

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "註冊成功!歡迎登入。")
        return redirect("users:login")
    return render(request, "users/register.html")


def login(request):
    if request.user.is_authenticated:
        return redirect("pages:home")

    if request.POST:
        user = authenticate(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login_user(request, user)
            # next是用來在登入後跳轉到指定URL的參數
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("pages:home")
        else:
            messages.error(request, "登入失敗，請重新登入一次。")
            return redirect("users:login")
    return render(request, "users/login.html")


@require_POST
@login_required
def logout(request):
    if hasattr(request, "_messages"):
        request._messages = FallbackStorage(request)

    logout_user(request)

    response = HttpResponse()
    response["HX-Redirect"] = "/"
    return response


@login_required
def profile(request):
    if request.POST:
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        # Debug: 印出表單驗證錯誤
        if not user_form.is_valid():
            print("User Form Errors:", user_form.errors)

        if not profile_form.is_valid():
            print("Profile Form Errors:", profile_form.errors)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "個人資料已成功更新")
            return redirect("users:profile")

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}

    return render(request, "users/profile.html", context)


@login_required
def user_dashboard(request):

    profile = request.user.profile
    user = request.user

    if profile.is_freelancer:
        return render(
            request,
            "users/freelancer_dashboard.html",
            {"profile": profile, "user": user},
        )

    else:

        return render(
            request, "users/client_dashboard.html", {"profile": profile, "user": user}
        )


@login_required
def apply_freelancer(request):
    profile = request.user.profile

    if request.POST:
        profile.is_freelancer = True
        profile.freelancer_verified = True
        profile.save()
        return redirect("users:user_dashboard")

    return render(request, "users/apply_freelancer.html")


# 忘記密碼
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = "/users/password_reset_done/"
    extra_context = {
        "protocol": settings.PROTOCOL,
        "domain": settings.DEFAULT_DOMAIN,
    }

    # 覆蓋郵件發送邏輯，避免重複發送郵件
    def form_valid(self, form):
        email = form.cleaned_data["email"]

        for user in form.get_users(email):
            context = {
                "email": email,
                "domain": settings.DEFAULT_DOMAIN,
                "protocol": settings.PROTOCOL,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            }
            subject = render_to_string(self.subject_template_name, context).strip()
            html_message = render_to_string(self.email_template_name, context)

            # 發送郵件
            email_msg = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_msg.content_subtype = "html"
            email_msg.send()

        # 不再調用的郵件發送邏輯
        return super(auth_views.PasswordResetView, self).form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = "/users/reset_done/"


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"


def switch_role(request):
    profile = request.user.profile
    if profile.is_freelancer:
        profile.is_freelancer = False
        profile.save()
    else:
        profile.is_freelancer = True
        profile.save()

    return redirect("users:user_dashboard")


@login_required
def feedback_view(request):
    profile = request.user.profile
    if profile.is_freelancer:
        comments_received = Comment.objects.filter(
            service__freelancer_user=request.user, is_deleted=False
        ).select_related("user", "service")
        context = {
            "comments_received": comments_received,
            "role": "freelancer",
        }
    else:
        comments_given = Comment.objects.filter(
            user=request.user, is_deleted=False
        ).select_related("service", "service__freelancer_user")
        context = {
            "comments_given": comments_given,
            "role": "client",
        }

    return render(request, "users/feedback.html", context)


@login_required
def feedback_view(request):
    """
    顯示用戶的評論（接案者看到收到的評論，業者看到發出的評論）
    """
    profile = request.user.profile
    if profile.is_freelancer:
        comments_received = Comment.objects.filter(
            service__freelancer_user=request.user, is_deleted=False
        ).select_related("user", "service")
        context = {
            "comments_received": comments_received,
            "role": "freelancer",
        }
    else:
        comments_given = Comment.objects.filter(
            user=request.user, is_deleted=False
        ).select_related("service", "service__freelancer_user")
        context = {
            "comments_given": comments_given,
            "role": "client",
        }

    return render(request, "users/feedback.html", context)


@login_required
def likes_view(request):
    """
    顯示用戶按愛心的服務
    """
    likes_given = Like.objects.filter(user=request.user).select_related(
        "service", "service__freelancer_user"
    )
    return render(request, "users/likes.html", {"likes_given": likes_given})


def mark_as_read_and_redirect(request, notification_id):
    if request.user.is_authenticated:
        notification = get_object_or_404(
            Notification, id=notification_id, recipient=request.user
        )
        notification.unread = False
        notification.save()

        # 返回 HX-Redirect 頭到通知的目標 URL
        return HttpResponse("", headers={"HX-Redirect": notification.get_target_url()})

    return JsonResponse({"status": "unauthorized"}, status=401)


@login_required
def freelancer_financial(request):
    orders = Order.objects.filter(service__freelancer_user=request.user).order_by(
        "-order_date"
    )

    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)

    total_income = orders.aggregate(total=Sum("total_price"))["total"] or 0

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)

    return render(
        request,
        "users/freelancer_financial.html",
        {"orders": orders, "total_income": total_income},
    )


@login_required
def purchased_services(request):
    user = request.user
    orders = Order.objects.filter(client_user=user).order_by("-order_date")

    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)

    return render(
        request,
        "users/purchased_services.html",
        {"orders": orders},
    )

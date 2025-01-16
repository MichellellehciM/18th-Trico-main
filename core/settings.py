import os
from dotenv import load_dotenv
from pathlib import Path
from ckeditor import *

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "*",
]

CSRF_TRUSTED_ORIGINS = [
    "https://trico.zeabur.app",
    "http://127.0.0.1:8000",
    f"https://{os.getenv('HOSTNAME')}",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_fsm",
    "users",
    "pages",
    "order",
    "services",
    "categories",
    "common",
    "comments",
    "django_ckeditor_5",
    "contact",
    "search",
    "notification",
    "taggit",
]
INSTALLED_APPS += [
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.line",
    "allauth.socialaccount.providers.google",
]
SITE_ID = 1


SOCIALACCOUNT_PROVIDERS = {
    "line": {
        "APP": {
            "client_id": os.getenv("LINE_CLIENT_ID"),
            "secret": os.getenv("LINE_SECRET"),
            "key": "",
        },
        "SCOPE": ["profile", "openid", "email"],
        "AUTH_PARAMS": {"response_type": "code"},
    },
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_SECRET"),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
}

LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_SIGNUP_REDIRECT_URL = "/"


SOCIALACCOUNT_LOGIN_ON_GET = True


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "notification.context_processors.unread_notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "zh-hant"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
COMPRESS_ROOT = BASE_DIR / "static"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)

AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = BASE_DIR / "media"
# CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional


STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "default_acl": AWS_DEFAULT_ACL,
            "querystring_auth": AWS_QUERYSTRING_AUTH,
            "object_parameters": AWS_S3_OBJECT_PARAMETERS,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
        },
    },
    "staticfiles": {  # 本地靜態文件儲存
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 設置gmail發送信件
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # django內建的郵件後端
EMAIL_HOST = "smtp.gmail.com"  # Gmail 的 SMTP 服務器
EMAIL_PORT = 587  # SMTP 服務器端口
EMAIL_USE_TLS = True  # 啟用 TLS 加密
EMAIL_USE_SSL = False  # 不使用 SSL 加密
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")  # Gmail 地址
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # Gmail 密碼
DEFAULT_FROM_EMAIL = "三合平台 <selinafs880504@gmail.com>"

# 替換 `DEFAULT_DOMAIN` 和 `PROTOCOL` 為您的開發環境
DEFAULT_DOMAIN = os.getenv("DEFAULT_DOMAIN")  # 本地開發使用
PROTOCOL = os.getenv("PROTOCOL", "http")  # 開發環境使用 http，生產使用 https


line_pay_hostname = os.getenv("HOSTNAME")

# 綠界金流相關配置
MERCHANT_ID = os.getenv("MERCHANT_ID")
HASH_KEY = os.getenv("HASH_KEY")
HASH_IV = os.getenv("HASH_IV")
ECPAY_URL = os.getenv("ECPAY_URL")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
LINE_CALLBACK_URL = os.getenv(
    "LINE_CALLBACK_URL", "http://localhost:8000/accounts/line/login/callback/"
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_SECRET")

# Google OAuth 回呼網址 (自動適應本地與 Zeabur)
DOMAIN = os.environ.get("DEFAULT_DOMAIN", "127.0.0.1:8000")
PROTOCOL = os.environ.get("PROTOCOL", "http")
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = (
    f"{PROTOCOL}://{DOMAIN}/accounts/google/login/callback/"
)

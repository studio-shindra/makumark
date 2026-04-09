from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# ALLOWED_HOSTS
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
    ALLOWED_HOSTS = [h for h in hosts.split(",") if h]

# CORS
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
else:
    origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [o for o in origins.split(",") if o]

# CSRF
csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o for o in csrf_origins.split(",") if o]

# Apple Sign-In / IAP
APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID", "")  # iOS Bundle ID, e.g. com.studioshindra.makumark
APPLE_SHARED_SECRET = os.environ.get("APPLE_SHARED_SECRET", "")  # App-Specific Shared Secret for /verifyReceipt
APPLE_IAP_PRODUCT_IDS = [
    p.strip() for p in os.environ.get(
        "APPLE_IAP_PRODUCT_IDS",
        "com.studioshindra.makumark.premium",
    ).split(",") if p.strip()
]
# DEBUG時のみ Apple 検証をスキップ可能（ローカル開発用）
APPLE_VERIFY_SKIP_IN_DEBUG = os.environ.get("APPLE_VERIFY_SKIP_IN_DEBUG", "1") == "1"




INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "import_export",
    "quotes",
    "tracking",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",   
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Postgres（docker-compose の環境変数を使用）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "makumark"),
        "USER": os.environ.get("POSTGRES_USER", "makuuser"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "makupass"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Heroku など DATABASE_URL がある環境ではそっちで上書き
# ただし、DEBUGモード（ローカル開発）の場合はローカルDBを優先
if "DATABASE_URL" in os.environ and not DEBUG:
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
    )

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ja"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "quotes.User"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

# ========== セキュリティヘッダー（本番時） ========== #
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
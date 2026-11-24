import os, dj_database_url
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
# Local development: read KEY=value lines from a .env file if one exists (real environment variables win).
_env = BASE_DIR / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.removeprefix("export ").split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))
E = os.environ.get
DEBUG = E("DEBUG") == "1"
SECRET_KEY = E("SECRET_KEY", "dev-only-change-me")
# On Vercel: *.vercel.app is allowed; add your own domain via ALLOWED_HOSTS="album.yourclub.co.ke"
CUSTOM = [h.strip() for h in E("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS = ["*"] if DEBUG else [".vercel.app", *CUSTOM]
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app", *[f"https://{h}" for h in CUSTOM]]
INSTALLED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "core"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware"]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",
        "core.views.site"]}}]
DATABASES = {"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=0)}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TIME_ZONE = "Africa/Nairobi"
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"}}
MEDIA_URL, MEDIA_ROOT = "/media/", BASE_DIR / "media"
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
# Site copy (set as environment variables)
CLUB_NAME = E("CLUB_NAME", "Our Club")
ALBUM_TITLE = E("ALBUM_TITLE", "Our New Album")
LAUNCH_DATE = E("LAUNCH_DATE", "this Saturday")
ALBUM_COVER = E("ALBUM_COVER", "")  # e.g. /static/img/cover.jpg or a full image URL
CONTACT_EMAIL, CONTACT_PHONE, LOCATION = E("CONTACT_EMAIL", ""), E("CONTACT_PHONE", ""), E("LOCATION", "Nairobi, Kenya")
SAYING = E("SAYING", "Pamoja tunaweza")
SAYING_EN = E("SAYING_EN", "Together we can")
CUSTOM_MIN = int(E("CUSTOM_MIN", "251"))
MAX_DOWNLOADS = int(E("MAX_DOWNLOADS", "15"))
DEMO_MODE = E("DEMO_MODE") == "1"  # skips payment; for previewing only
R2_ACCOUNT_ID, R2_KEY, R2_SECRET, R2_BUCKET = (E("R2_ACCOUNT_ID", ""), E("R2_KEY", ""), E("R2_SECRET", ""), E("R2_BUCKET", ""))

# Payments: Baraka API (Baraka calls Safaricom Daraja for us)
BARAKA_API_URL = E("BARAKA_API_URL", "https://baraka.sdabaraka.org/api/v1")
BARAKA_API_TOKEN, BARAKA_FUND_ID = E("BARAKA_API_TOKEN", ""), E("BARAKA_FUND_ID", "")
BARAKA_ACCOUNT_REF, BARAKA_DESCRIPTION = E("BARAKA_ACCOUNT_REF", "LAUNCH"), E("BARAKA_DESCRIPTION", "Ambassadors")
BARAKA_CALLBACK_SECRET = E("BARAKA_CALLBACK_SECRET", "")   # long random string; becomes part of the callback address
BARAKA_CALLBACK_BASE = E("BARAKA_CALLBACK_BASE", "")       # public https address of THIS site; needed when testing locally

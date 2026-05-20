import os
import time
from .settings import *

ENV = os.getenv("DJANGO_ENV", "prod")
print(f"[local_settings] ENV = {ENV}")

# ========================
# DATABASE
# ========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('POSTGRES_NAME', 'mediacms'),
        "HOST": os.getenv('POSTGRES_HOST', 'postgres'),
        "PORT": os.getenv('POSTGRES_PORT', '5432'),
        "USER": os.getenv('POSTGRES_USER', 'mediacms'),
        "PASSWORD": os.getenv('POSTGRES_PASSWORD', 'mediacms'),
        "OPTIONS": {'pool': True},
    }
}

# ========================
# REDIS / CELERY
# ========================
REDIS_LOCATION = os.getenv('REDIS_LOCATION', 'redis://redis:6379/1')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
BROKER_URL = REDIS_LOCATION
CELERY_RESULT_BACKEND = REDIS_LOCATION


# ========================
# COMMON
# ========================
DO_NOT_TRANSCODE_VIDEO = os.getenv('DO_NOT_TRANSCODE_VIDEO', 'False') == 'True'
MP4HLS_COMMAND = "/home/mediacms.io/bento4/bin/mp4hls"
FRONTEND_HOST = os.getenv('FRONTEND_HOST', 'http://localhost')
PORTAL_NAME = os.getenv('PORTAL_NAME', 'MediaCMS')
REGISTER_ALLOWED = False

# ========================
# PROFILE DEFINITIONS
# ========================

def dev_config():
    print("[local_settings] Running in DEV mode")

    middleware = [
        m for m in MIDDLEWARE
        if m != 'deploy.docker.protected_media.ProtectedMediaMiddleware'
    ]

    middleware.append("deploy.docker.dev_auth.DevAutoLoginMiddleware")

    return {
        "DEBUG": True,
        "USE_IDENTITY_PROVIDERS": False,
        "USE_RBAC": False,
        "GLOBAL_LOGIN_REQUIRED": False,
        "LOGIN_URL": "/",
        "LOGIN_REDIRECT_URL": "/",
        "LOGOUT_REDIRECT_URL": "/",
        "ALLOW_CUSTOM_MEDIA_URLS": True,
        "MIDDLEWARE": middleware,
        "INSTALLED_APPS": [
            app for app in INSTALLED_APPS
            if app != "allauth.socialaccount.providers.openid_connect"
        ],
    }


def read_secret(
        path="/secrets/mediacms_client_secret",
        timeout=2000,
        interval=10,
):
    start = time.time()

    while True:
        if os.path.exists(path):
            with open(path) as f:
                secret = f.read().strip()
                if secret:
                    print("[OIDC] Secret loaded")
                    return secret

        if time.time() - start > timeout:
            raise RuntimeError(f"Secret not found: {path}")

        time.sleep(interval)


def prod_config():
    print("[local_settings] Running in PROD mode")

    oidc_secret = read_secret()
    is_https = FRONTEND_HOST.startswith("https")
    oidc_base_url = os.getenv(
        "OIDC_BASE_URL",
        "http://auth-server:8080/realms/record-manager"
    )

    middleware = list(MIDDLEWARE)

    if os.getenv("PROTECTED_MEDIA_ENABLED", "True") == "True":
        if 'deploy.docker.protected_media.ProtectedMediaMiddleware' not in middleware:
            middleware.append('deploy.docker.protected_media.ProtectedMediaMiddleware')
    if 'deploy.docker.by_md5.ByMd5Middleware' not in middleware:
        middleware.append('deploy.docker.by_md5.ByMd5Middleware')
    if 'deploy.docker.by_id.ByIdMiddleware' not in middleware:
        middleware.append('deploy.docker.by_id.ByIdMiddleware')

    config = {
        "DEBUG": os.getenv('DEBUG', 'False') == 'True',
        "USE_IDENTITY_PROVIDERS": True,
        "USE_RBAC": True,
        "GLOBAL_LOGIN_REQUIRED": True,
        "ALLOW_CUSTOM_MEDIA_URLS": True,
        "LOGIN_URL": "/accounts/oidc/keycloak/login/",
        "LOGIN_REDIRECT_URL": "/",
        "LOGOUT_REDIRECT_URL": "/accounts/oidc/keycloak/login/",
        "CSRF_TRUSTED_ORIGINS": [os.getenv('FRONTEND_HOST', 'http://localhost')],
        "INSTALLED_APPS": INSTALLED_APPS + [
            "allauth.socialaccount.providers.openid_connect",
        ],
        "MIDDLEWARE": middleware,
        "SOCIALACCOUNT_PROVIDERS": {
            "openid_connect": {
                "APPS": [
                    {
                        "provider_id": "keycloak",
                        "name": "Keycloak",
                        "client_id": os.getenv("OIDC_CLIENT_ID", "mediacms"),
                        "secret": oidc_secret,
                        "settings": {
                            "server_url": os.getenv(
                                "OIDC_SERVER_URL",
                                f"{oidc_base_url}/.well-known/openid-configuration",
                            ),
                        },
                    }
                ]
            }
        },
        "SOCIALACCOUNT_ADAPTER": "deploy.docker.oidc_adapter.RoleRestrictedSocialAccountAdapter",
        "MEDIACMS_ROLE_MAPPING": {
            os.getenv("MEDIACMS_READ_ROLE",  "read-media-role"):  "user",
            os.getenv("MEDIACMS_WRITE_ROLE", "write-media-role"): "advancedUser",
            os.getenv("MEDIACMS_ADMIN_ROLE", "admin-media-role"): "admin",
        },
        "MEDIACMS_ROLE_PRIORITY": [
            os.getenv("MEDIACMS_ADMIN_ROLE", "admin-media-role"),
            os.getenv("MEDIACMS_WRITE_ROLE", "write-media-role"),
            os.getenv("MEDIACMS_READ_ROLE",  "read-media-role"),
        ],
        "CAN_ADD_MEDIA": os.getenv("CAN_ADD_MEDIA", "advancedUser"),
        "PROTECTED_MEDIA_ENABLED": os.getenv("PROTECTED_MEDIA_ENABLED", "True") == "True",
        "OIDC_USERINFO_URL": os.getenv(
            "OIDC_USERINFO_URL",
            f"{oidc_base_url}/protocol/openid-connect/userinfo",
        ),
        "UPLOAD_MAX_SIZE": int(os.getenv("UPLOAD_MAX_SIZE", str(1024 * 1024 * 1024))),
        "UPLOAD_MAX_FILES_NUMBER": int(os.getenv("UPLOAD_MAX_FILES_NUMBER", "100")),
        "NUMBER_OF_MEDIA_USER_CAN_UPLOAD": int(os.getenv("NUMBER_OF_MEDIA_USER_CAN_UPLOAD", "100")),
    }

    if is_https:
        config["SECURE_PROXY_SSL_HEADER"] = ("HTTP_X_FORWARDED_PROTO", "https")

    return config

# ========================
# PROFILE DISPATCH
# ========================

PROFILES = {
    "dev": dev_config,
    "prod": prod_config,
}

if ENV not in PROFILES:
    raise RuntimeError(f"Unknown DJANGO_ENV: {ENV}")

config = PROFILES[ENV]()
globals().update(config)


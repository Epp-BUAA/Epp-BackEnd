"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-@pywj-yjew^uh$e(dzt5t4+rq27vwp@k4q@#x&+icla+ppvu^x"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    'business'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 设置跨域SESSION配置，本地测试时需要SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'None'
CORS_ALLOW_CREDENTIALS = True

# 配置为true会出问题
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:10516',
    'http://127.0.0.1:10516',
    'https://epp.buaase.cn',
]

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

ROOT_URLCONF = "backend.urls"

RESOURCE_PATH = os.path.join(BASE_DIR, 'resource')

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        #  'ENGINE': 'django.db.backends.sqlite3',
        #  'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '2024_EPP',
        'USER': 'root',
        'PASSWORD': 'RuanGong-0601-G5',
        'HOST': '114.116.214.56',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/resource/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'resource')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USER_AVATARS_PATH = 'resource/uploads/users/avatars'  # 用户头像相对路径
USER_DOCUMENTS_PATH = 'resource/uploads/users/documents'  # 用户上传文件路径
USER_REPORTS_PATH = 'resource/database/users/reports'  # 用户生成报告路径
USER_SEARCH_CONSERVATION_PATH = 'resource/database/users/conversation/search'  # 调研助手对话文件路径
USER_READ_CONSERVATION_PATH = 'resource/database/users/conversation/read'  # 论文研读助手对话文件路径
USER_READ_MAP_PATH = 'resource/database/users/conversation/read/file_reading_2_tmp_kb_id_map.json'
PAPERS_PATH = 'resource/database/papers/'  # 数据库论文路径
BATCH_DOWNLOAD_PATH = 'resource/database/users/batch_download'  # 批量下载文件路径

PAPERS_URL = 'resource/database/papers/'  # 数据库论文本地URL
BATCH_DOWNLOAD_URL = '/resource/database/users/batch_download/'  # 批量下载文件本地URL
USER_DOCUMENTS_URL = '/resource/uploads/users/documents/'  # 用户上传文件本地URL
CACHE_PATH = '/cache/'  # 缓存路径

MAX_Similarity = 0.8  # 最大相似度，介于-1和1之间，不确定

# 远程模型部署开放的API接口
REMOTE_MODEL_BASE_PATH = '172.17.62.88:7861'
# 使用openai流式接口调用glm3大模型，不附带知识库
REMOTE_CHATCHAT_GLM3_OPENAI_PATH = '172.17.62.88:20005'


# 语义检索相关
VECTOR_DIM = 1024
LOCAL_VECTOR_DATABASE_PATH = 'resource/vector_database_for_search/'
LOCAL_FAISS_NAME = "paper_index.faiss"
LOCAL_METADATA_NAME = "paper_metadata.pkl"

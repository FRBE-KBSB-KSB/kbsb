#    Copyright 2018 Ruben Decrop
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os

ALLOWED_HOSTS = ['*']

APPEND_SLASH = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHESSAPI_URL = 'https://chessapi.bycco.be/'

CMS_LANGUAGES = {
    1: [
        {
            'code': 'nl',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': 'nl',
            'public': True,
        },
        {
            'code': 'en',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': 'en',
            'public': True,
        },
        {
            'code': 'fr',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': 'fr',
            'public': True,
        },
        {
            'code': 'de',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': 'de',
            'public': True,
        }

    ],
    'default': {
        'redirect_on_fallback': True,
        'hide_untranslated': False,
        'public': True,
    },
}

CMS_PERMISSION = False

CMS_PLACEHOLDER_CONF = {}

CMS_TEMPLATES = (
    ('vuecms.html', 'Cms Page'),
    ('vuelanding.html', 'Landing Page'),
    ('page.html', 'Plain Page'),
)

DATABASES = {   
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'kbsb',
        'USER': 'kbsb',
    }
}

DATA_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True

DJANGOCMS_STYLE_CHOICES = ['logo-wrapper', 'imgwidth100']

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

INSTALLED_APPS = [

    # django + cms admin
    'djangocms_admin_style',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    # djangocms
    'cms',
    'filer',
    'easy_thumbnails',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_style',
    'djangocms_file',
    'djangocms_googlemap',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_text_ckeditor',

    # local
    'webpack_loader',
    'rd_django',
    'kbsbarticles',
    'kbsbmembers',
    'kbsbdoc',
    'kbsb',
]

LANGUAGE_CODE = 'nl'
LANGUAGES = (
    ('nl', 'nl'),
    ('en', 'en'),
    ('fr', 'fr'),
    ('de', 'de')
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'kbsb': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'kbsbdoc': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'kbsbarticles': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'kbsbmembers': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'formatter': 'detailed',
        },        
        'rd_django': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
MEDIA_URL = '/media/'

META_SITE_PROTOCOL = 'https'
META_USE_SITES = True

MIDDLEWARE = [
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'
]

MIGRATION_MODULES = {

}

PHPBASEURL =  '/'

PRODUCTION = True

ROOT_URLCONF = 'kbsb.urls'

SECRET_KEY = 'You know, a weakness here and ther, just a little bit of pressure'

SITE_ID = 1

STATIC_ROOT = 'static'
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'kbsb', 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings',
                'kbsb.context_processor.local',
                'kbsbdoc.context_processor.choices',
            ],
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            #     # 'django.template.loaders.eggs.Loader'
            # ],
        },
    },
]

TEMPLATE_SETTINGS = [
    'PRODUCTION', 'PHPBASEURL',
]

THUMBNAIL_PROCESSORS = (
   'easy_thumbnails.processors.colorspace',
   'easy_thumbnails.processors.autocrop',
   #'easy_thumbnails.processors.scale_and_crop',
   'filer.thumbnail_processors.scale_and_crop_with_subject_location',
   'easy_thumbnails.processors.filters',
)

TIME_ZONE = 'Europe/Brussels'

USE_I18N = True
USE_L10N = True
USE_TZ = True

WSGI_APPLICATION = 'kbsb.wsgi.application'

try:
    from local_settings import *
except ImportError:
    print('No local settings found')
    pass

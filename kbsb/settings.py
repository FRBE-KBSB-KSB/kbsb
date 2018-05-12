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

_ = lambda s: s

ALLOWED_HOSTS = ['*']

APPEND_SLASH = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CMS_LANGUAGES = {
    1: [
        {
            'code': 'nl',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': _('nl'),
            'public': True,
        },
        {
            'code': 'en',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': _('en'),
            'public': True,
        },
        {
            'code': 'fr',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': _('fr'),
            'public': True,
        },
        {
            'code': 'de',
            'redirect_on_fallback': True,
            'hide_untranslated': False,
            'name': _('de'),
            'public': True,
        }

    ],
    'default': {
        'redirect_on_fallback': True,
        'hide_untranslated': False,
        'public': True,
    },
}

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {
    'content': {
        'language_fallback': False,
    },
}

CMS_TEMPLATES = (
    ('cms.html', _('CMS page')),
    ('cms_sidebar.html', _('CMS with sidebar')),
    ('landing.html', _('CMS landing page')),
    ('page.html', _('Page')),
)

DATA_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False

DJANGOCMS_STYLE_CHOICES = ['logo-wrapper']

EMAIL_HOST = '127.0.0.1'
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
    'django_tablib',

    # djangocms
    'cms',
    'filer',
    'easy_thumbnails',
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_image',
    'cmsplugin_filer_teaser',
    'cmsplugin_filer_utils',
    'cmsplugin_filer_video',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'djangocms_style',
    'djangocms_file',
    'djangocms_googlemap',
    'djangocms_inherit',
    'djangocms_link',
    'reversion',

    # blog
    'aldryn_apphooks_config',
    'aldryn_categories',
    'aldryn_common',
    'aldryn_events',
    'aldryn_newsblog',
    'aldryn_people',
    'aldryn_translation_tools',
    'appconf',
    'bootstrap3',
    'extended_choices',
    'parler',
    'standard_form',
    'sortedm2m',
    'taggit',

    # local
    'webpack_loader',
    'rd_django',
    'kbsb'
]

LANGUAGE_CODE = 'nl'
LANGUAGES = (
    ('nl', _('nl')),
    ('en', _('en')),
    ('fr', _('fr')),
    ('de', _('de'))
)

LOCALE_PATHS = (os.path.join(BASE_DIR, 'i18n'),)

MEDIA_ROOT = os.path.join(DATA_DIR, 'media')
MEDIA_URL = '/media/'

MIDDLEWARE_CLASSES = [
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

PARLER_LANGUAGES = {
    1: (
        {'code': 'nl',},
        {'code': 'en',},
        {'code': 'fr',},
        {'code': 'de',},
    ),
    'default': {
        'fallbacks': ['nl', 'fr', 'de'],
    }
}

ROOT_URLCONF = 'kbsb.urls'

SECRET_KEY = 'Ewelmerci,zukkedikkewosten'

SITE_ID = 1

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'kbsb', 'static'),
)

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
            ],
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            #     'django.template.loaders.eggs.Loader'
            # ],
        },
    },
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

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'static/',
        'STATS_FILE': os.path.join(BASE_DIR, 'frontend', 'webpack-stats.json')
    }
}

WSGI_APPLICATION = 'kbsb.wsgi.application'

try:
    from local_settings import *
except ImportError:
    print('No local settings found')
    pass
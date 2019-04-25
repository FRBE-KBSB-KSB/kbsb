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

from cms.sitemaps import CMSSitemap

from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from .views import testpost, testget, testpage1, testpage2

# import cdmembers.urls
# import cdmembers.urls_apimembers

admin.autodiscover()

urlpatterns = [
    path('sitemap.xml', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(

    # next url pattern has a negative lookahead pattern
    # to avoid redirecting 404s in /api/* to /{locale}/api/*
    re_path(r'^(?!api)(?!koskmembers)', include('cms.urls')),    

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



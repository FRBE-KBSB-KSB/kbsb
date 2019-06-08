#    Copyright 2017 - 2018 Ruben Decrop
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

import logging
log = logging.getLogger(__name__)

import simplejson as json
import datetime
import os.path

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf import settings # import the settings file

from .models import (
    KbsbDocument, KbsbDocGroupView, KbsbPhpLinkView,
)

@plugin_pool.register_plugin
class KbsbDocGroupPlugin(CMSPluginBase):

    model = KbsbDocGroupView
    name = 'Group of documents'
    module = 'FRBE-KBSB'
    render_template = 'kbsbdoc/group.html'

    def render(self, context, instance, placeholder):
        docs = KbsbDocument.objects.all()
        if instance.category:
            docs = docs.filter(category=instance.category)
        if instance.topic:
            docs = docs.filter(topic=instance.topic)        
        if instance.doctype:
            docs = docs.filter(doctype=instance.doctype)
        if instance.locale:
            docs = docs.filter(locale=instance.locale)
        docs = list(docs.order_by('-topicdate'))
        for d in docs:
            d.url = os.path.join(settings.MEDIA_URL, 'docs', d.category, 
                d.slug)
        context['docs'] = docs
        context['title'] = instance.grouptitle
        return super(KbsbDocGroupPlugin, self).render(
            context, instance, placeholder) 

@plugin_pool.register_plugin
class KbsbPhpLinkPlugin(CMSPluginBase):

    model = KbsbPhpLinkView
    name = 'Link to php site'
    module = 'FRBE-KBSB'
    render_template = 'kbsbdoc/phplink.html'

    def render(self, context, instance, placeholder):
        context['label'] = instance.label
        context['url'] = instance.url
        return super(KbsbPhpLinkPlugin, self).render(
            context, instance, placeholder) 

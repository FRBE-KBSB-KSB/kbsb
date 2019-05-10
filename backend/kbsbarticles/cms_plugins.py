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
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf import settings # import the settings file
from django import forms


from .models import (
    KbsbMarkdownView
)

@plugin_pool.register_plugin
class KbsbMarkdownPlugin(CMSPluginBase):

    model = KbsbMarkdownView
    name = 'Markdown page'
    module = 'FRBE-KBSB'
    render_template = 'kbsbarticles/markdown.html'

    def render(self, context, instance, placeholder):
        context['source'] = instance.source
        context['sanitize'] = instance.sanitize
        return super(KbsbMarkdownPlugin, self).render(
            context, instance, placeholder)            
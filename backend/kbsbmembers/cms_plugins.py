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
    KbsbMember, KbsbGroupNames, KbsbMember, KbsbMemberView, KbsbGroupView,
)

@plugin_pool.register_plugin
class KbsbMemberPlugin(CMSPluginBase):

    model = KbsbMemberView
    name = 'Member'
    module = 'FRBE-KBSB'
    render_template = 'kbsbmembers/member.html'

    def render(self, context, instance, placeholder):
        m = KbsbMember.objects.get(idbel=instance.idbel)
        if m:
            context['first_name'] = m.first_name
            context['last_name'] = m.last_name
            context['photourl'] = ''  
            context['mobiletel'] = m.mobiletel
            context['email'] = m.email
        else:
            context['first_name'] = 'Member not found'
        return super(KbsbMemberPlugin, self).render(
            context, instance, placeholder)


@plugin_pool.register_plugin
class KbsbGroupPlugin(CMSPluginBase):

    model = KbsbGroupView
    name = 'Group'
    module = 'FRBE-KBSB'
    render_template = 'kbsbmembers/group.html'

    def render(self, context, instance, placeholder):
        ms = []
        for m in KbsbMember.objects.all():
            roles = json.loads(m.roles)
            for r in roles:
                if r.get('groupname') == instance.groupname:
                    ms.append(m)
        context['members'] = ms
        return super(KbsbGroupPlugin, self).render(
            context, instance, placeholder)            
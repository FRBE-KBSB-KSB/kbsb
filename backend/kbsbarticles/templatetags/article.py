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


import logging
log = logging.getLogger(__name__)

from django import template
register = template.Library()

import markdown2 


from kbsbarticles.models import KbsbArticle

@register.inclusion_tag('kbsbarticles/tag_intro.html', takes_context=True)
def article_intro(context, *args, **kwargs):
    lang = context.get('LANGUAGE_CODE')
    articles = KbsbArticle.objects.all().order_by('-created')
    artlist = []
    for a in articles:
        for al in a.localefields.all():
            if al.locale == lang:
                artlist.append({
                    'title': al.title, 
                    'intro': markdown2.markdown(al.intro),       
                })
                break
        else:
            artlist.append({
                'title': a.maintitle, 
                'intro': 'Language not available',       
            })
    return {
        "articles": artlist,
        "backgroundcolor": 'green lighten-2',
        "titlecolor": 'black',
    }

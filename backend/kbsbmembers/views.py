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

from django.http import HttpResponse, HttpResponseNotFound
from .models import KbsbMember


def testphoto(request):
    with open('loaded.png', 'rb') as f:
        img = f.read()
        return HttpResponse(img, content_type="image/png")

def memberphoto(request, id):
    try:
        m = KbsbMember.objects.get(id=id)
        return HttpResponse(bytes(m.badgeimage), content_type=m.badgemimetype)
    except KbsbMember.DoesNotExist:
        return HttpResponseNotFound('Photo not found')


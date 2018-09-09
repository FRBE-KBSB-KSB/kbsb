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

import requests
import simplejson as json
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render


# Create your views here.

def testpost(request):
    ruben = {
        'first_name': 'Ruben',
        'last_name': 'Decrop',
        'gender': 'M',
        'email': 'ruben@decrop.net',
        'mobile': '+32477571313',
        'idbel': '45608',
        'org': [{
            'group': 'board',
            'function': 'webmaster',
        }]
    }
    ca = settings.CHESSAPI_URL
    rs = requests.post("{}/members/member".format(ca), data=json.dumps(ruben))
    return HttpResponse('Ruben Decrop POST request done: {}'.format(rs.json))


def testget(request, idbel):
    ca = settings.CHESSAPI_URL
    rs = requests.get("{}/members/member/{}".format(ca, idbel))
    return HttpResponse('Ruben Decrop POST request done: {}'.format(rs.text))

def testpage1(request):
    return render(request, 'testpage1.html')

def testpage2(request):
    return render(request, 'testpage2.html')


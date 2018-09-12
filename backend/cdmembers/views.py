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
from django.shortcuts import render
from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, JSONRenderer

def to_int(s, default):
    """
    convert s to integer , returning default if failing
    :param s: str
    :param default: int
    :return: an int
    """
    try:
        return int(s)
    except:
        return default

class ImageRenderer(BaseRenderer):
    media_type = 'image/*'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

@api_view(['GET', 'POST'])
def members_all(request):
    url = "{}/members/member".format(settings.CHESSAPI_URL)

    if request.method == 'GET':
        rs = requests.get(url)
        if rs.status_code == 200:
            data = rs.json()
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK, data=dict(members=data))

    if request.method == 'POST':
        rs = requests.post(url, json=request.data)
        if rs.status_code == 201:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=rs.status_code)

@api_view(['GET', 'PUT', 'DELETE'])
def members_one(request, idbel):

    url = "{}/members/member/{}".format(settings.CHESSAPI_URL, idbel)

    if request.method == 'PUT':
        rs = requests.put(url, json=request.data)
        if rs.status_code == 200:
            data = rs.json()
            return Response(status=status.HTTP_200_OK, data=dict(members=data))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=rs.status_code)


def admin_members(request):
    return render(request, 'cdmembers/admin_members.html')


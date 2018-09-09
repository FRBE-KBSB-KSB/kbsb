# Copyright Ruben Decrop

import logging
log = logging.getLogger(__name__)

import requests
import simplejson as json
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

@api_view(['GET'])
def getMembers(request):
    ca_url = "{0}members/member".format(settings.CHESSAPI_URL)
    resp = requests.get(ca_url)
    if resp.status_code == 200:
        data = resp.json()
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_200_OK, data=data)


# Copyright Ruben Decrop

import logging
log = logging.getLogger(__name__)

import requests
import iso8601
import datetime
import simplejson as json
import os, os.path

from binascii import a2b_base64
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, JSONRenderer

from .models import KbsbDocument

def datetostr(d):
    """
    return a isostr from a date or None
    """
    if d:
        return d.strftime("%Y-%m-%d %H:%M:%S")

def strtodate(s):
    """
    return a datetime from a isodate(time) str or None
    """
    if isinstance(s, str):
        s = s.split('T')[0].split(' ')[0]
    try:
        return iso8601.parse_date(s)
    except iso8601.ParseError:
        return

def querytoint(s, default=0):        
    """
    convert query patameter to int 
    with default
    """
    try:
        return int(request.GET.get(s, default))
    except:
        return default

@api_view(['POST', 'GET'])
def docs_all(request):

    if request.method == 'GET':
        docs = KbsbDocument.objects.all()
        category = request.GET.get('category')
        if category:
            docs = docs.filter(category=category)
        topic = request.GET.get('topic')
        if topic:
            docs = docs.filter(topic=topic)        
        doctype = request.GET.get('doctype')
        if doctype:
            docs = docs.filter(doctype=doctype)
        locale = request.GET.get('locale')
        if locale:
            docs = docs.filter(locale=locale)
        start = querytoint('start')    
        count = querytoint('count', 25)    
        ds = [
            {
                'id': d.id,
                'category': d.category,
                'doctype': d.doctype,
                'locale': d.locale,
                'mimetype': d.mimetype,
                'name': d.name,
                'slug': d.slug,
                'topic': d.topic,
                'topicdate': datetostr(d.topicdate),
                'uploaded': datetostr(d.uploaded),
                'url': os.path.join(settings.MEDIA_URL, 'docs', d.category, d.slug),
            } for d in docs[start:start+count]
        ]
        return Response(dict(documents=ds))

    if request.method == 'POST':
        """
        upload a new document 
        """
        doc = request.data.get('document', {})
        # process filcontent
        filecontent = doc.get('filecontent')
        if not filecontent:
            return Response('FilecontentMissing', 
                status=status.HTTP_400_BAD_REQUEST)
        fileheader, filebody = filecontent.split(',')
        filebinary = a2b_base64(filebody)
        # create ans save new KbsbDocument
        d = KbsbDocument()
        d.archived = doc.get('archived', False)
        d.category = doc.get('category', 'other')
        d.doctype = doc.get('doctype', 'other')
        d.doclength = len(filebinary)
        d.locale = doc.get('locale', '')
        d.mimetype = fileheader.split(':')[1].split(';')[0]
        d.name = doc.get('name', '')
        d.slug = doc.get('slug')
        d.topic = doc.get('topic', '')
        d.topicdate = strtodate(doc.get('topicdate'))
        d.uploaded = datetime.datetime.utcnow()
        if not d.slug:
            return Response('SlugMissing', 
                status=status.HTTP_400_BAD_REQUEST)
        try:
            d.save()
        except Exception:
            log.exception('Saving to db')
            return Response('DocNotSaved', 
                status=status.HTTP_400_BAD_REQUEST)
        # write binary file
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'docs', d.category))
        except FileExistsError:
            pass
        with open(os.path.join(settings.MEDIA_ROOT, 'docs', d.category, d.slug), 'wb') as f:
            f.write(filebinary)
        # return
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def docs_one(request, id):

    try:
        d = KbsbDocument.objects.get(id=id)
    except KbsbDocument.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        ds = {
            'id': d.id,
            'archived': d.archived,
            'category': d.category,
            'doclength': d.doclength,
            'doctype': d.doctype,
            'locale': d.locale,
            'mimetype': d.mimetype,
            'name': d.name, 
            'slug': d.slug,
            'topicdate': datetostr(d.topicdate),
            'topic': d.topic,
            'uploaded': datetostr(d.uploaded),
        }
        return Response(dict(document=ds))

    # if request.method == 'PUT':
    #     data = request.data.get('member', {})
    #     m.birthdate = strtodate(data.get('birthdate')) or  m.birthdate
    #     m.chesstitle = data.get('chesstitle', m.chesstitle)
    #     m.email = data.get('email', m.email)
    #     m.federation = data.get('federation', m.federation)
    #     m.first_name = data.get('first_name', m.first_name)
    #     m.gender = data.get('gender', m.gender)
    #     m.idbel = data.get('idbel', m.idbel)
    #     m.idclub = data.get('idclub', m.idclub)
    #     m.idfide = data.get('idefide', m.idfide)
    #     m.last_name = data.get('last_name', m.last_name)
    #     m.locale = data.get('locale', m.locale)
    #     m.mobiletel = data.get('mobiletel', m.mobiletel)
    #     m.nationalitybel = data.get('nationalitybele', m.nationalitybel)
    #     m.nationalityfide = data.get('nationalityfide', m.nationalityfide)
    #     try:
    #         m.privacy = json.dumps(data.get('privacy'))
    #     except:
    #         pass
    #     m.remarks = data.get('remarks', m.remarks)
    #     m.roles = json.dumps(data.get('roles')) or '[]'
    #     try:
    #         m.save()
    #         ms = {
    #             'id': m.id,
    #             'birthdate': datetostr(m.birthdate),
    #             'chesstitle': m.chesstitle,
    #             'email': m.email,
    #             'federation': m.federation,
    #             'first_name': m.first_name,
    #             'gender': m.gender, 
    #             'idclub': m.idclub,
    #             'idbel': m.idbel,
    #             'idfide': m.idfide,
    #             'last_name': m.last_name,
    #             'locale': m.locale,
    #             'mobiletel': m.mobiletel,
    #             'nationalitybel': m.nationalitybel, 
    #             'nationalityfide': m.nationalityfide,
    #             'privacy': json.loads(m.privacy),
    #             'remarks': m.remarks,
    #             'roles': json.loads(m.roles),
    #         }
    #         return Response(dict(member=ms), status=status.HTTP_200_OK)
    #     except Exception as e:
    #         log.exception("could not update member")
    #         return Response(e, status=status.HTTP_406_NOT_ACCEPTABLE)
        
    if request.method == 'DELETE':
        f =  os.path.join(settings.MEDIA_ROOT, 'docs', d.category, d.slug)
        os.remove(f)
        d.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



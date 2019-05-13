# Copyright Ruben Decrop

import logging
log = logging.getLogger(__name__)

import requests
import iso8601
import simplejson as json

from binascii import a2b_base64
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, JSONRenderer

from .models import KbsbMember, KbsbGroupNames, KbsbRoleNames

class ImageRenderer(BaseRenderer):
    media_type = 'image/*'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

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

@api_view(['POST', 'GET'])
def member_all(request):

    if request.method == 'GET':
        members = KbsbMember.objects.all()
        ms = [
            {
                'id': m.id,
                'first_name': m.first_name,
                'last_name': m.last_name,
            } for m in members
        ]
        return Response(dict(members=ms))

    if request.method == 'POST':
        """
        member should contain: idbel
        member can contain: mobiletel, birthdate, email 
        """
        data = request.data.get('member', {})
        idbel = data.get('idbel', '')
        bp = {}
        if idbel:
            idbel = idbel.lstrip('0')
            ca_url = "{0}ranking/bel/{1}".format(settings.CHESSAPI_URL, idbel)
            resp = requests.get(ca_url)
            if resp.status_code != 200:
                return Response('ChessapiConnectionIssue', 
                    status=status.HTTP_400_BAD_REQUEST)
            bp = resp.json()
        try:
            p = KbsbMember.objects.get(idbel=idbel)
            return Response('MemberNotSaved', 
                status=status.HTTP_400_BAD_REQUEST)
        except KbsbMember.DoesNotExist:
            pass
        m = KbsbMember()
        m.birthdate = strtodate(bp.get('birthdate'))
        m.chesstitle = bp.get('chesstitle') or ''
        m.email = data.get('email') or ''
        m.federation = bp.get('federation', '')
        m.first_name = bp.get('first_name', data.get('first_name', ''))
        m.gender = bp.get('gender', data.get('gender', 'M'))
        m.idbel = idbel
        m.idclub = bp.get('idclub', '')
        m.idfide = bp.get('idfide', '')
        m.last_name = bp.get('last_name', data.get('last_name', ''))
        m.locale = data.get('locale', 'nl')
        m.mobiletel = data.get('mobiletel') or ''
        m.nationalitybel = bp.get('nationality', 'BEL')
        m.privacy = '{}'
        m.remarks = ''
        m.roles = '[]'
        try:
            m.save()
            return Response(dict(id=m.id))
        except Exception:
            log.exception('Saving to db')
            return Response('MemberNotSaved', status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def member_detail(request, id):

    try:
        m = KbsbMember.objects.get(id=id)
    except KbsbMember.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        ms = {
            'id': m.id,
            'birthdate': datetostr(m.birthdate),
            'chesstitle': m.chesstitle,
            'email': m.email,
            'federation': m.federation,
            'first_name': m.first_name,
            'gender': m.gender, 
            'idclub': m.idclub,
            'idbel': m.idbel,
            'idfide': m.idfide,
            'last_name': m.last_name,
            'locale': m.locale,
            'mobiletel': m.mobiletel,
            'nationalitybel': m.nationalitybel, 
            'nationalityfide': m.nationalityfide,
            'privacy': json.loads(m.privacy),
            'remarks': m.remarks,
            'roles': json.loads(m.roles),
        }
        return Response(dict(member=ms))

    if request.method == 'PUT':
        data = request.data.get('member', {})
        m.birthdate = strtodate(data.get('birthdate')) or  m.birthdate
        m.chesstitle = data.get('chesstitle', m.chesstitle)
        m.email = data.get('email', m.email)
        m.federation = data.get('federation', m.federation)
        m.first_name = data.get('first_name', m.first_name)
        m.gender = data.get('gender', m.gender)
        m.idbel = data.get('idbel', m.idbel)
        m.idclub = data.get('idclub', m.idclub)
        m.idfide = data.get('idefide', m.idfide)
        m.last_name = data.get('last_name', m.last_name)
        m.locale = data.get('locale', m.locale)
        m.mobiletel = data.get('mobiletel', m.mobiletel)
        m.nationalitybel = data.get('nationalitybele', m.nationalitybel)
        m.nationalityfide = data.get('nationalityfide', m.nationalityfide)
        try:
            m.privacy = json.dumps(data.get('privacy'))
        except:
            pass
        m.remarks = data.get('remarks', m.remarks)
        m.roles = json.dumps(data.get('roles')) or '[]'
        try:
            m.save()
            ms = {
                'id': m.id,
                'birthdate': datetostr(m.birthdate),
                'chesstitle': m.chesstitle,
                'email': m.email,
                'federation': m.federation,
                'first_name': m.first_name,
                'gender': m.gender, 
                'idclub': m.idclub,
                'idbel': m.idbel,
                'idfide': m.idfide,
                'last_name': m.last_name,
                'locale': m.locale,
                'mobiletel': m.mobiletel,
                'nationalitybel': m.nationalitybel, 
                'nationalityfide': m.nationalityfide,
                'privacy': json.loads(m.privacy),
                'remarks': m.remarks,
                'roles': json.loads(m.roles),
            }
            return Response(dict(member=ms), status=status.HTTP_200_OK)
        except Exception as e:
            log.exception("could not update member")
            return Response(e, status=status.HTTP_406_NOT_ACCEPTABLE)
        
    if request.method == 'DELETE':
        m.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def member_photo(request, id):

    try:
        m = KbsbMember.objects.get(id=id)
    except KbsbMember.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    photo = request.data.get('photo')
    if photo:
        try:
            header, data = photo.split(',')
            log.info('header photo %s', header)
            m.badgemimetype = header.split(':')[1].split(';')[0]
            m.badgeimage = a2b_base64(data)
            m.badgelength = len(m.badgeimage)
            m.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def grouproles(request):

    if request.method == 'GET':
        grps = KbsbGroupNames.objects.all()
        groupnames = [{
            'shortname': g.shortname,
            'name': g.name,
            'translations': json.loads(g.translations)
        } for g in grps]
        rls = KbsbRoleNames.objects.all()        
        rolenames = [{
            'shortname': r.shortname,
            'name': r.name,
            'translations': json.loads(r.translations)
        } for r in rls]
        return Response(dict(rolenames=rolenames, groupnames=groupnames))

    if request.method == 'PUT':
        groupnames = request.data.get('groupnames')
        rolenames = request.data.get('rolenames')
        # prepare as much as possible before the old records are deleted
        # and the new records are saved
        if groupnames is None or rolenames is None:
            return Response('MissingParameter', 
                status=status.HTTP_400_BAD_REQUEST)
        oldgroupsid = [ g.id for g in KbsbGroupNames.objects.all()]
        oldrolesid = [ r.id for r in KbsbRoleNames.objects.all()]
        grps = []
        rls = []
        for g in groupnames:
            try:
                gt = json.dumps(g.get('translations')) or "{}"
            except Exception:
                return Response('InvalidTranslations', 
                    status=status.HTTP_400_BAD_REQUEST)
            go = KbsbGroupNames()
            go.shortname = g.get('shortname', '')
            go.name = g.get('name', '')
            go.translations = gt          
            grps.append(go)
        for r in rolenames:
            try:
                rt = json.dumps(r.get('translations')) or "{}"
            except Except:
                return Response('InvalidTranslations', 
                    status=status.HTTP_400_BAD_REQUEST)
            ro = KbsbRoleNames()
            ro.shortname = r.get('shortname', '')
            ro.name = r.get('name', '')
            ro.translations = rt  
            rls.append(ro) 
        for id in oldgroupsid: 
            KbsbGroupNames.objects.filter(id=id).delete()
        for id in oldrolesid: 
            KbsbRoleNames.objects.filter(id=id).delete()
        for g in grps:
            g.save()
        for r in rls:
            r.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
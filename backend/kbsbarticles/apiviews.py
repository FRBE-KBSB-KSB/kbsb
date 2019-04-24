# Copyright Ruben Decrop

import logging
log = logging.getLogger(__name__)

import requests
import iso8601
import simplejson as json
from binascii import a2b_base64
from django.db.models import Max
from django.shortcuts import redirect
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer, JSONRenderer

from .models import (
    KbsbMember,
    KbsbMemberRole,
)

from .serializers import (
    MemberBasicSerializer,
    MemberDetailSerializer,
)

@api_view(['POST', 'GET'])
def member_all(request):

    if request.method == 'GET':
        members = KbsbMember.objects.all()
        ms = MemberBasicSerializer(members, many=True)
        return Response(ms.data)

    if request.method == 'POST':
        """
        member should contain: idbel
        member can contain: mobiletel, birthdate, email 
        """
        data = request.data.get('member', {})
        idbel = data.get('idbel', '')
        if idbel:
            idbel = idebel.lstrip('0')
            ca_url = "{0}ranking/bel/{1}".format(settings.CHESSAPI_URL, idbel)
            resp = requests.get(ca_url)
            if resp.status_code != 200:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            bp = resp.json()
            idfide = bp.get('idfide', '')
            fp = {}
            if idfide:
                ca_url = "{0}ranking/fide/{1}".format(settings.CHESSAPI_URL,
                                                    idfide)
                resp = requests.get(ca_url)
                if resp.status_code == 200:
                    fp = resp.json()
        try:
            p = KbsbMember.objects.get(idbel=idbel)
        except KbsbMember.DoesNotExist:
            p = KbsbMember()
        if 'birthdate' in data:
            birthdate = data.get('birthdate')
            if birthdate:
                p.birthdate = iso8601.parse_date(birthdate)
            else:
                p.birthdate = None            
        p.chesstitle = bp.get('chesstitle') or ''
        p.email = data.get('email') or ''
        p.federation = bp.get('federation')
        p.first_name = bp.get('first_name')
        p.gender = bp.get('gender')
        p.idclub = bp.get('idclub')
        p.idfide = idfide
        p.idbel = idbel
        p.last_name = bp.get('last_name')
        p.locale = request.LANGUAGE_CODE.lower()[:2]
        p.mobiletel = data.get('mobiletel') or ''
        p.nationalityfide = fp.get('nationalityfide', '')
        p.nationalitybel = bp.get('nationalitybel')
        p.privacy = data.get('privacy', '')
        p.ratingbel = bp.get('currentrating')
        p.ratingfide = fp.get('currentrating', 0)
        p.remarks = data.get('remarks') or ''
        try:
            p.save()
            ms = MemberDetailSerializer(p)
        except Exception as e:
            log.exception('Saving to db')
            return Response('MemberNotSaved', status=status.HTTP_400_BAD_REQUEST)
        return Response(dict(member=ms.data))

@api_view(['GET', 'PUT', 'DELETE'])
def member_detail(request, pk):

    try:
        p = KbsbMember.objects.get(pk=pk)
    except KbsbMember.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        ms = MemberDetailSerializer(p)
        return Response(dict(member=ms.data))

    if request.method == 'PUT':
        data = request.data.get('member', {})
        if 'birthdate' in data:
            birthdate = data.get('birthdate')
            if birthdate:
                p.birthdate = iso8601.parse_date(birthdate)
            else:
                p.birthdate = None            
        p.chesstitle = data.get('chesstitle', p.chesstitle)
        p.email = data.get('email', p.email)
        p.federation = data.get('federation', p.federation)
        p.first_name = data.get('first_name', p.first_name)
        p.gender = data.get('gender', p.gender)
        p.idbel = data.get('idbel', p.idbel)
        p.idfide = data.get('idefide', p.idfide)
        p.last_name = data.get('last_name', p.last_name)
        p.locale = data.get('locale', p.locale)
        p.mobiletel = data.get('mobiletel', p.mobiletel)
        p.nationalitybel = data.get('nationalitybele', p.nationalitybel)
        p.nationalityfide = data.get('nationalityfide', p.nationalityfide)
        p.ratingbel = data.get('ratingbel', p.ratingbel)
        p.ratingfide = data.get('ratingfide', p.ratingfide)
        p.remarks = data.get('remarks', p.remarks)
        try:
            p.save()
            ms = MemberDetailSerializer(p)
            return Response(dict(member=ms.data), status=status.HTTP_200_OK)
        except Exception as e:
            log.exception("could not update member")
            return Response(e, status=status.HTTP_406_NOT_ACCEPTABLE)
        
    if request.method == 'DELETE':
        p.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@renderer_classes((ImageRenderer, JSONRenderer))
def member_photo(request, idsub):

    try:
        member = KbsbMember.objects.get(pk=idsub)
    except KbsbMember.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(content_type=member.badgemimetype,
                        data=member.badgeimage)

    if request.method == 'POST':
        photo = request.data.get('photo')
        if photo:
            try:
                header, data = photo.split(',')
                member.badgemimetype = header.split(':')[1].split(';')[0]
                member.badgeimage = a2b_base64(data)
                member.badgelength = len(member.badgeimage)
                member.save()
                return Response(status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# chess player

@api_view(['GET'])
def belplayer(request, idbel):

    """fetch belgian rating details"""

    idbel = idbel.lstrip('0')
    ca_url = "{0}ranking/bel/{1}".format(settings.CHESSAPI_URL, idbel)
    resp = requests.get(ca_url)
    details = {}
    if resp.status_code == 200:
        details.update(resp.json())
        details['idbel'] = details['_id']
        return Response(details)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def fideplayer(request, idfide):

    idfide = idfide.lstrip('0')
    ca_url = "{0}ranking/fide/{1}".format(settings.CHESSAPI_URL, idfide)
    resp = requests.get(ca_url)
    details = {}
    if resp.status_code == 200:
        details.update(resp.json())
        details['idfide'] = details['_id']
        return Response(details)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


    if request.method == 'PUT':
        data = request.data.get('attendee', {})
        if 'birthdate' in data:
            birthdate = data.get('birthdate')
            if birthdate:
                p.birthdate = iso8601.parse_date(birthdate)
            else:
                p.birthdate = None            
        p.category = data.get('category', p.category)
        p.chesstitle = data.get('chesstitle', p.chesstitle)
        p.confirmed = data.get('confirmed', p.confirmed)
        p.emailparent = data.get('emailparent', p.emailparent)
        p.emailplayer = data.get('emailplayer', p.emailplayer)
        p.first_name = data.get('first_name', p.first_name)
        p.fullnameattendant = data.get('fullnameattendant', p.fullnameattendant)
        p.fullnameparent = data.get('fullnameparent', p.fullnameparent)
        p.gender = data.get('gender', p.gender)
        p.idbel = data.get('idbel', p.idbel)
        p.idfide = data.get('idefide', p.idfide)
        p.last_name = data.get('last_name', p.last_name)
        p.locale = data.get('locale', p.locale)
        p.meals = data.get('meals', p.meals)
        p.mobileattendant = data.get('mobileattendant', p.mobileattendant)
        p.mobileparent = data.get('mobileparent', p.mobileparent)
        p.mobileplayer = data.get('mobileplayer', p.mobileplayer)
        p.nationalityfide = data.get('nationalityfide', p.nationalityfide)
        p.payamount = int(data.get('payamount', p.payamount))
        p.paymessage = data.get('paymessage', p.paymessage)
        log.info('data attendee %s', data)
        # p.paydate = data.get('paydate')
        if 'present' in data:
            present = data.get('present')
            if present:
                p.present = iso8601.parse_date(present)
            else:
                p.present = None
        p.rating = data.get('rating', p.rating)
        p.ratingbel = data.get('ratingbel', p.ratingbel)
        p.ratingfide = data.get('ratingfide', p.ratingfide)
        p.remarks = data.get('remarks', p.remarks)
        p.custom1 = data.get('custom1', p.custom1)
        try:
            p.save()
            return Response(dict(id=p.id),
                            status=status.HTTP_200_OK)
        except Exception as e:
            log.exception("could not update attendee")
            return Response(e, status=status.HTTP_406_NOT_ACCEPTABLE)

    if request.method == 'DELETE':
        try:
            p.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(e, status=status.HTTP_406_NOT_ACCEPTABLE)


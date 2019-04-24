# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

from django.conf.urls import url
from kbsbmembers import apiviews

urlpatterns = [
    url(r'members$', apiviews.member_all),
    url(r'members/(?P<id>\w+)$', apiviews.member_detail),
    url(r'members/(?P<idb>[0-9]+)/photo$', apiviews.member_photo),
    url(r'belplayer/(?P<idbel>[0-9]+)$', apiviews.belplayer),
    url(r'belplayer/(?P<idbel>[0-9]+)/photo$', apiviews.belplayer_photo),
    url(r'fideplayer/(?P<idfide>[0-9]+)$', apiviews.fideplayer),
]

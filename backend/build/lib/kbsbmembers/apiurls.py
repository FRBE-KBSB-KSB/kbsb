# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

from django.urls import path, re_path
from kbsbmembers import apiviews

urlpatterns = [
    path('members', apiviews.member_all),
    path('members/<int:id>', apiviews.member_detail),
    path('members/<int:id>/photo', apiviews.member_photo),
    path('grouproles', apiviews.grouproles),
    # path('belplayer/<slug:idbel>', apiviews.belplayer),
    # path('belplayer/<slug:idebl>/photo$', apiviews.belplayer_photo),
]

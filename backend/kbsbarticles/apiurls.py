# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

from django.conf.urls import url
from kbsbarticles import apiviews

urlpatterns = [
    url(r'articles$', apiviews.article_all),
    url(r'articles/(?P<id>\w+)$', apiviews.article_one),
]

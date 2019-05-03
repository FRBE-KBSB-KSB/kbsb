# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

from django.conf.urls import url
from kbsbarticles import views

urlpatterns = [
    url(r'articles$', views.articlespage),
    url(r'articles/(?P<slug>\w+)$', views.articlepage),
]

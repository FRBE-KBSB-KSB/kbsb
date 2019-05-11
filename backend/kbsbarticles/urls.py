# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

from django.urls import path
from kbsbarticles import views

urlpatterns = [
    path('list', views.articlespage),
    path('view/<slug:slug>', views.articlepage),
]

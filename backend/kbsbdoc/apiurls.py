# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

from django.urls import path, re_path
from .apiviews import docs_all, docs_one

urlpatterns = [
    path('docs', docs_all),
    path('docs/<int:id>', docs_one),
]

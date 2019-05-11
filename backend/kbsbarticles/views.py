# Copyright Ruben Decrop

import logging
log = logging.getLogger(__name__)

from django.shortcuts import render
from kbsbarticles.models import KbsbArticle

def articlespage(request):
    return render(request, 'kbsbarticles/articles.html')
 
def articlepage(request, slug):
    try:
        art = KbsbArticle.objects.get(slug=slug)
    except KbsbArticle.DoesNotExist:
        return render(request, 'kbsbarticles/notfound.html')
    return render(request, 'kbsbarticles/article.html', {'id': art.id})

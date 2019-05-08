# Copyright Ruben Decrop

import logging
log = logging.getLogger(__name__)

from django.shortcuts import render
from kbsbarticles.models import KbsbArticle

def articlespage(request):
    return render(request, 'kbsbarticle/articles.html')
 
def articlepage(request, slug):
    try:
        art = KbsbArticle.ojects.get(slug=slug)
    except KbsbArticle.DoesNotExist:
        return render(request, 'kbsbarticle/notfound.html')
    return render(request, 'kbsbarticle/article.html')

#    Copyright 2018 Ruben Decrop
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0


from django.db.models import *
from django.utils import timezone

class KbsbArticle(Model):

    author = CharField("Author", max_length=80)
    created = DateTimeField(editable=False)
    archived = DateTimeField("Archive date", null=True)
    mainlocale = CharField("Main language", max_length=80)
    maintitle = CharField("Title in main language", max_length=80)
    modified = DateTimeField()
    readmore = BooleanField('Read more shown', default=False)
    published = DateTimeField("Publication date", null=True)
    slug = CharField('Slug', max_length=80)  

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(KbsbArticle, self).save(*args, **kwargs)

class KbsbArticleLocale(Model):
    article = ForeignKey(KbsbArticle, on_delete=CASCADE, null=True, 
        related_name='localefields')
    locale = CharField("Locale", max_length=5)
    content = TextField('Content')
    intro = TextField('Intro')
    title = CharField("Title", max_length=80)

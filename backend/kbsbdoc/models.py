#    Copyright 2018 Ruben Decrop
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0


import logging
log = logging.getLogger(__name__)

import datetime

from django.db.models import ( 
    Model, 
    CharField, DateField, IntegerField, TextField, DateTimeField, SlugField,
    BooleanField,
) 
from cms.models.pluginmodel import CMSPlugin

class KbsbDocument(Model):

    archived = BooleanField('Archived', default=False)
    category = CharField(max_length=80)             # CA_RVB, AG_AV, ...
    doclength = IntegerField('Length')
    doctype = CharField(max_length=80)              # word, pdf, ...
    locale = CharField("Locale", max_length=5)      # nl, fr, ... all
    mimetype = CharField(max_length=80)           
    name = CharField("Name", max_length=80)
    slug = SlugField(unique=True)
    topic = CharField(max_length=80)             # report, invitation, ....
    topicdate = DateField('Topic date', null=True)
    uploaded = DateTimeField('Upload date', null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.uploaded = datetime.datetime.utcnow()
        super(KbsbDocument, self).save(*args, **kwargs)

class KbsbDocGroupView(CMSPlugin):

    all = [('', 'Tous - Alle')]
    localechoices = [
        ('nl', 'nl'),
        ('fr', 'fr'),
        ('de', 'de'),
        ('en', 'en'),
        ('fr-nl', 'français + nederlands'),
        ('other', 'Autre - Andere'),
    ]
    doctypechoices = [
        ('docx', 'Ms Word  file'),
        ('xlsx', 'Ms Excel file'),
        ('pptx', 'Ms Powerpoint file'),
        ('odt', 'Libreoffice writer file'),
        ('ods', 'Libreoffice calc file'),
        ('odp', 'Libreoffice impress file'),
        ('pdf', 'PDF file'),
        ('md', 'Markdown file'),
        ('zip', 'Zip file'),
        ('other', 'Autre - Andere')
    ]
    doccategorychoices = [
        ('ca-rvb', "Conseil d'Administration - Raad van Bestuur"),
        ('ag-av', "Assemblée générale - Algemene vergadering"),
        ('cis', "CIS arbitres - scheidsrechters"),
        ('dispute', "Comité de litiges - Geschillencommissie"),
        ('appeal', "Comité d'appel - Beroepscommissie"),
        ('other', 'Autre - Andere'),
    ]
    topicchoices = [
        ('report', 'Rapport - Verslag'),
        ('invitation', 'Invitation - Uitnodiging'),
        ('annex', 'Ficher en annexe - Bestand in bijlage'),
        ('other', 'Autre - Andere'),
    ]

    category = CharField('Event', max_length=40, choices=all+doccategorychoices)
    topic = CharField('Topic', max_length=40, choices=all+topicchoices)
    doctype = CharField('Document type', max_length=40, choices=all+doctypechoices)
    year = IntegerField('Year', default=2019)
    locale = CharField('Language', max_length=5, choices=localechoices)
    archived = BooleanField('Archived', default=False)
    start = IntegerField('Start index Document', default=0)
    count = IntegerField('Number of documents', default=25)

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
from dataclasses import dataclass, astuple, asdict

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

@dataclass
class TextValue:
    value: str
    text: str

catchoices = [
    TextValue( 'ca-rvb', "Conseil d'Administration - Raad van Bestuur"),
    TextValue( 'ag-av',"Assemblée générale - Algemene vergadering"),
    TextValue( 'cis', "CIS arbitres - scheidsrechters"),
    TextValue( 'dispute', "Comité de litiges - Geschillencommissie"),
    TextValue( 'appeal', "Comité d'appel - Beroepscommissie"),
    TextValue( 'other', "Autre - Andere"),
]

doctypechoices = [
    TextValue('docx', 'Ms Word  file'),
    TextValue('xlsx', 'Ms Excel file'),
    TextValue('pptx', 'Ms Powerpoint file'),
    TextValue('odt', 'Libreoffice writer file'),
    TextValue('ods', 'Libreoffice calc file'),
    TextValue('odp', 'Libreoffice impress file'),
    TextValue('pdf', 'PDF file'),
    TextValue('md', 'Markdown file'),
    TextValue('zip', 'Zip file'),
    TextValue('other', 'Autre - Andere')
]

localechoices = [
    TextValue('nl', 'nl'),
    TextValue('fr', 'fr'),
    TextValue('de', 'de'),
    TextValue('en', 'en'),
    TextValue('fr-nl', 'français + nederlands'),
    TextValue('other', 'Autre - Andere'),
]

topicchoices = [
    TextValue('report', 'Rapport - Verslag'),
    TextValue('invitation', 'Invitation - Uitnodiging'),
    TextValue('annex', 'Ficher en annexe - Bestand in bijlage'),
    TextValue('other', 'Autre - Andere'),
]

allchoice = [TextValue('', 'Tous - Alle')]

class KbsbDocGroupView(CMSPlugin):

    grouptitle = CharField('Group title', max_length=80)
    category = CharField('Event', max_length=40, blank=True,
        choices=[astuple(tv) for tv in  allchoice + catchoices])
    topic = CharField('Topic', max_length=40,  blank=True,
        choices=[astuple(tv) for tv in  allchoice + topicchoices])
    doctype = CharField('Document type', max_length=40,  blank=True,
        choices=[astuple(tv) for tv in  allchoice + doctypechoices])
    locale = CharField('Language', max_length=5,  blank=True,
        choices=[astuple(tv) for tv in  allchoice + localechoices])
    archived = BooleanField('Archived', default=False)

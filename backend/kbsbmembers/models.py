#    Copyright 2018 Ruben Decrop
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from django.db.models import ( 
    Model, 
    BinaryField, CharField, DateField, IntegerField, TextField,
    ForeignKey,
    CASCADE,
) 

class KbsbMember(Model):

    badgeimage = BinaryField("Badge image", blank=True)
    badgelength = IntegerField("Length badge image", blank=True, default=0)
    badgemimetype = CharField("Badge mimetype", blank=True, default='', max_length=20)
    birthdate = DateField("Birthdate", null=True)
    chesstitle = CharField("Chess title", max_length=4, blank=True, default='')
    email = CharField("Email", max_length=40, blank=True, default='')
    federation = CharField("Federation", max_length=4, blank=True)
    first_name = CharField("First name", max_length=25)
    gender = CharField("Gender", max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    idclub = CharField("Club id", max_length=4, blank=True)
    idfide = CharField("FIDE id", max_length=15, blank=True)
    idbel = CharField("Belgian id", max_length=6, unique=True)
    last_name = CharField("Last name", max_length=40)
    locale = CharField("Locale", max_length=5)
    mobiletel = CharField("Mobile phone", max_length=15, blank=True, default='')
    nationalitybel = CharField("Nationality on passport", max_length=4, blank=True)
    nationalityfide = CharField("Nationality for FIDE", max_length=4, blank=True)
    privacy = TextField('Privacy Restrictions (JSON)', default='{}')  # jsonfield
    remarks = TextField("Remarks", blank=True)
    roles = TextField('Roles (JSON)', default= '{}')   # json field

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

class KbsbGroupNames(Model):
    shortname = CharField('Abbreviated group name', max_length=25)
    name = CharField('Long group name', max_length=80)
    translations = TextField('Translations (JSON)')

class KbsbRoleNames(Model):
    shortname = CharField('Abbreviated role name', max_length=25)
    name = CharField('Long role name ', max_length=80)
    translations = TextField('Translations (JSON)')

#    Copyright 2018 Ruben Decrop
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0


from django.db.models import *

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
    locale = CharField("Locale", max_length=5)
    mobiletel = CharField("Mobile phone", max_length=15, blank=True, default='')
    last_name = CharField("Last name", max_length=40)
    nationalitybel = CharField("Nationality on passport", max_length=4, blank=True)
    nationalityfide = CharField("Nationality for FIDE", max_length=4, blank=True)
    privacy = CharField('Privacy Restrictions', max_length=255, default='')
    ratingbel = IntegerField("Belgian rating", default=0)
    ratingfide = IntegerField("FIDE rating", default=0)
    remarks = TextField("Remarks", blank=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

class KbsbMemberRole(Model):
    member = ForeignKey(KbsbMember, on_delete=CASCADE, null=True, 
        related_name='roles')
    groupname = CharField('Name of the group', max_length=40)
    rolename = CharField('Name of role', max_length=40)  
        # only english names like 'President', 'Secretary'
        # translation is done at client side 
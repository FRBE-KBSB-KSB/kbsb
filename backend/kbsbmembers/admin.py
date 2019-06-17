#    Copyright 2018 Ruben Decrop
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

import logging
log = logging.getLogger(__name__)

from django.contrib.admin import ModelAdmin
from django.forms import ModelForm

from .models import KbsbMemberView, KbsbGroupView, KbsbGroupNames

class KbsbMemberViewForm(ModelForm):
    class Meta:
        model = KbsbMemberView
        fields = ['idbel', 'groupname']

    def __init__(self, *args, **kwargs):
        super(KbsbMemberViewForm, self).__init__(*args, **kwargs)
        choices = [(x.id, x.name) for x in KbsbGroupNames.objects.all()]
        self.fields['groupnam'].choices = choices

class KbsbMemberViewAdmin(ModelAdmin):
    form = KbsbMemberViewForm

class KbsbGroupViewForm(ModelForm):
    class Meta:
        model = KbsbGroupView
        fields = ['groupname']

    def __init__(self, *args, **kwargs):
        super(KbsbGroupViewForm, self).__init__(*args, **kwargs)
        choices = [(x.id, x.name) for x in KbsbGroupNames.objects.all()]
        self.fields['groupnam'].choices = choices

class KbsbGroupViewAdmin(ModelAdmin):
    form = KbsbGroupViewForm

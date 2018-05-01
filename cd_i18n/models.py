# copyright Ruben Decrop

from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models.pluginmodel import CMSPlugin

class CdTranslationAvailable(CMSPlugin):
    nl = models.BooleanField(default=False, verbose_name=_('Dutch version available'))
    fr = models.BooleanField(default=False, verbose_name=_('French version available'))
    de = models.BooleanField(default=False, verbose_name=_('German version available'))
    en = models.BooleanField(default=False, verbose_name=_('English version available'))

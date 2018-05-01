# copyright Ruben Decrop

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import CdTranslationAvailable

@plugin_pool.register_plugin
class CdI18nPlugin(CMSPluginBase):

    model = CdTranslationAvailable
    name = _("Available Translations")
    render_template = "cd_i18n/available_languages.html"
    cache = False

    def render(self, context, instance, placeholder):
        context['lang'] = context['targetlang'] if 'targetlang' in context \
            else context['language']
        context = super(CdI18nPlugin, self).render(
            context, instance, placeholder)
        return context

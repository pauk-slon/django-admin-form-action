from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ExtendedActionsConfig(AppConfig):
    name = 'extended_actions'
    verbose_name = _('Administration: Extended Actions')

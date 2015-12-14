# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("Wprowadź poprawny adres email oraz hasło. "
                           "Uwaga: wielkość liter ma znaczenie."),
        'inactive': _("Konto nie zostało aktywowane"),
    }

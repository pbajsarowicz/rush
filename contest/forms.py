# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
)
from django.utils.translation import ugettext_lazy as _

from contest.models import RushUser


class RegistrationForm(forms.ModelForm):
    """
    Form for new user registration.
    """

    class Meta:
        model = RushUser
        fields = [
            'email', 'first_name', 'last_name', 'organization_name',
            'organization_address',
        ]


class LoginForm(AuthenticationForm):
    """
    Build-in form to log user in. Overwriting error_messages
    to make them more clear for user.
    """
    error_messages = {
        'invalid_login': _(
            'Wprowadź poprawny login oraz hasło. '
            'Uwaga: wielkość liter ma znaczenie.'
        ),
        'inactive': _('Konto nie zostało aktywowane'),
    }


class SettingPasswordForm(SetPasswordForm):
    """
    Form for setting user's password.
    """
    error_messages = {
        'password_mismatch': _('Hasła nie są identyczne.'),
    }
    new_password1 = forms.CharField(
        label=_('Nowe hasło'),
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label=_('Powtórz hasło'),
        widget=forms.PasswordInput
    )

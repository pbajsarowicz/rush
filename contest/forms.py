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
        'username_appears': _('Podana nazwa użytkownika jest już zajęta.')
    }
    username = forms.CharField(label=_('Nazwa użytkownika'))
    new_password1 = forms.CharField(
        label=_('Hasło'),
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label=_('Powtórz hasło'),
        widget=forms.PasswordInput
    )
    field_order = ['username', 'new_password1', 'new_password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if RushUser.objects.filter(username=username):
                raise forms.ValidationError(
                    self.error_messages['username_appears'],
                    code='username_appears',
                )
        return username

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        username = self.cleaned_data.get('username')
        self.user.set_password(password)
        self.user.username = username
        if commit:
            self.user.save()
        return self.user

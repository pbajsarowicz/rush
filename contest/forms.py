# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
)
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

from contest.models import RushUser, Club


class RegistrationForm(forms.ModelForm):
    """
    Form for new user registration.
    """
    club_code = forms.CharField(
        validators=[
            RegexValidator(r'^\d{5}$', 'Kod klubowy musi zwierać 5 cyfr')
        ]
    )

    class Meta:
        model = RushUser
        fields = (
            'email', 'first_name', 'last_name', 'organization_name',
            'organization_address', 'club_code',
        )

    def save(self, commit=True):
        """
        Handles assigning club to a user.
        """
        user = super(RegistrationForm, self).save(commit=False)
        club_code = self.cleaned_data['club_code']
        club, __ = Club.objects.get_or_create(code=club_code)
        user.club = club
        user.save()


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

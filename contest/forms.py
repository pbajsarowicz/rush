# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
)
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

from contest.models import (
    Contestant,
    Club,
    RushUser,
    Contest,
)


class RegistrationForm(forms.ModelForm):
    """
    Form for new user registration.
    """
    club_code = forms.CharField(
        label='Kod klubowy',
        max_length=5,
        required=False,
        validators=[
            RegexValidator(r'^\d{5}$', 'Kod klubowy musi zwierać 5 cyfr')
        ],
        widget=forms.TextInput(attrs={'class': 'invisible'})
    )

    def save(self, commit=True):
        """
        Handles assigning club to a user.
        """
        user = super(RegistrationForm, self).save(commit=False)
        club_code = self.cleaned_data['club_code']

        if club_code:
            club, __ = Club.objects.get_or_create(code=club_code)
            user.club = club

        user.save()

    class Meta:
        model = RushUser
        fields = (
            'email', 'first_name', 'last_name', 'organization_name',
            'organization_address', 'club_code',
        )


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
        if RushUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                self.error_messages['username_appears'],
                code='username_appears',
            )
        return username

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        username = self.cleaned_data['username']
        self.user.set_password(password)
        self.user.username = username
        if commit:
            self.user.save()
        return self.user


class ContestantForm(forms.ModelForm):
    """
    Form for contestant creation.
    """
    def __init__(self, *args, **kwargs):
        self.contest = kwargs.pop('contest_id')
        super(ContestantForm, self).__init__(*args, **kwargs)

    def clean_age(self):
        age = self.cleaned_data.get('age')
        contest = Contest.objects.get(pk=self.contest)
        if contest.age_min <= age <= contest.age_max:
            return age
        raise forms.ValidationError(
            'Zawodnik nie mieści się w wymaganym przedziale wiekowym.'
        )


    class Meta:
        model = Contestant
        fields = (
            'first_name', 'last_name', 'gender',
            'age', 'school', 'styles_distances',
        )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
)
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

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
        user.username = uuid.uuid4()
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


class ResetPasswordSendEmailForm(forms.ModelForm):
    """
    Form that send form with link to reset password
    """
    email = forms.EmailField(
        label='email',
        required=True)

    class Meta:
        model = RushUser
        fields = ['email']


class ResetPasswordForm(SetPasswordForm):
    """
    Form for reset user's password.
    """
    error_messages = {
        'password_mismatch': _('Hasła nie są identyczne.'),
    }
    new_password1 = forms.CharField(
        label=_('Hasło'),
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label=_('Powtórz hasło'),
        widget=forms.PasswordInput
    )
    field_order = ['new_password1', 'new_password2']


class ContestForm(forms.ModelForm):
    """
    Form for creating Contests.
    """

    def __init__(self, *args, **kwargs):
        super(ContestForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs = {'class': 'datetime'}
        self.fields['deadline'].widget.attrs = {'class': 'datetime'}
        self.fields['description'].widget.attrs = {
            'class': 'materialize-textarea'
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now():
            raise forms.ValidationError(
                'Data zawodów nie może być wcześniejsza niż dzień dzisiejszy.'
            )
        return date

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        date = self.cleaned_data.get('date')
        if deadline < timezone.now():
            raise forms.ValidationError(
                'Termin dodawania zwodników musi być dłuższy niż podana data.'
            )
        elif deadline > date:
            raise forms.ValidationError(
                'Ostateczny termin dodawania zawodników nie może być później '
                'niż data zawodów.'
            )
        return deadline

    def clean_age_max(self):
        age_min = self.cleaned_data.get('age_min')
        age_max = self.cleaned_data.get('age_max')

        if age_min > age_max:
            raise forms.ValidationError(
                'Przedział wiekowy jest niepoprawny. '
                'Popraw wartości i spróbuj ponownie.'
            )
        return age_max

    class Meta:
        model = Contest
        fields = [
            'date', 'place', 'deadline', 'age_min',
            'age_max', 'description', 'organizer'
        ]

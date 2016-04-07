# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
    PasswordResetForm,
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


class RushResetPasswordForm(SetPasswordForm):
    """
    Form for resetting user's password.
    """
    error_messages = {
        'password_mismatch': _('Hasła nie są identyczne.'),
        'username_appears': _('Podana nazwa użytkownika jest już zajęta.')
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

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)

        if commit:
            self.user.save()

        return self.user


class RushSetPasswordForm(RushResetPasswordForm):
    """
    Form for setting user's password.
    """
    username = forms.CharField(label=_('Nazwa użytkownika'))

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
        self.user = super(RushSetPasswordForm, self).save(commit=False)

        username = self.cleaned_data['username']
        self.user.username = username

        if commit:
            self.user.save()

        return self.user


class RushResetPasswordEmailForm(PasswordResetForm):
    """
    Form that sends form with link to reset password.
    """
    def __init__(self, *args, **kwargs):
        super(RushResetPasswordEmailForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not RushUser.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(
                'Konto dla podanego adresu nie istnieje lub nie zostało '
                'jeszcze aktywowane. Sprawdź poprawność podanego adresu. '
                'W razie problemów skontaktuj się z nami {}'.format(
                    settings.SUPPORT_EMAIL
                )
            )
        return email

    def send_email(self, request):
        """
        Sends an email with a link which lets reset a password.
        """
        email = self.cleaned_data['email']
        for user in self.get_users(email):
            user.send_reset_password_email(request)


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

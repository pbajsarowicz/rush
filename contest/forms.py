# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from contest.models import (
    Club,
    Contest,
    Contestant,
    School,
    RushUser,
)


YEARS_RANGE = 41
current_year = datetime.now().year
year_dropdown = [
    (year, year,) for year in xrange(
        current_year, current_year - YEARS_RANGE, -1
    )
]


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
        organization = self.cleaned_data['organization_name']

        if club_code:
            unit, created = Club.objects.get_or_create(code=club_code)
            if created:
                unit.name = organization
                unit.save()
        else:
            unit, __ = School.objects.get_or_create(name=organization)
        user.content_type = ContentType.objects.get_for_model(unit)
        user.object_id = unit.id

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

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            if '@' in username:
                username = RushUser.objects.get(email=username).username
            self.user_cache = authenticate(
                username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RushResetPasswordForm(SetPasswordForm):
    """
    Form for resetting user's password.
    """
    new_password1 = forms.CharField(
        label=_('Nowe Hasło'),
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label=_('Powtórz hasło'),
        widget=forms.PasswordInput
    )

    error_messages = {
        'password_mismatch': _('Hasła nie są identyczne.'),
    }
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
    new_password1 = forms.CharField(
        label=_('Hasło'),
        widget=forms.PasswordInput
    )
    username = forms.CharField(label=_('Nazwa użytkownika'))

    field_order = ['username', 'new_password1', 'new_password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if RushUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'Podana nazwa użytkownika jest już zajęta.'
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
    organization = forms.CharField(label='Klub/Szkoła', max_length=100)
    styles = forms.CharField(max_length=128, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.contest = kwargs.pop('contest_id')
        self.user = kwargs.pop('user')
        super(ContestantForm, self).__init__(*args, **kwargs)

        if self.user.unit:
            self.fields['organization'].initial = self.user.unit
            self.fields['organization'].widget.attrs['readonly'] = True
        self.fields['year_of_birth'] = forms.ChoiceField(choices=year_dropdown)

    def clean_year_of_birth(self):
        year_of_birth = int(self.cleaned_data.get('year_of_birth'))
        contest = Contest.objects.get(pk=self.contest)
        if contest.lowest_year <= year_of_birth <= contest.highest_year:
            return year_of_birth
        raise forms.ValidationError(
            'Zawodnik nie mieści się w wymaganym przedziale wiekowym.'
        )

    def clean_styles(self):
        styles = self.cleaned_data.get('styles')
        return styles.split(',')

    def save(self, commit=True):
        contestant = super(ContestantForm, self).save(commit=False)

        contestant.styles = self.cleaned_data['styles']

        if commit:
            contestant.save()
        return contestant

    class Meta:
        model = Contestant
        fields = (
            'first_name', 'last_name', 'gender',
            'year_of_birth', 'school'
        )


class ContestForm(forms.ModelForm):
    """
    Form for creating Contests.
    """
    organization = forms.CharField(label='Organizacja', max_length=255)
    styles = forms.CharField(max_length=128, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')

        super(ContestForm, self).__init__(*args, **kwargs)

        self.fields['styles'].widget.attrs = {'id': 'styles-summary'}
        self.fields['date'].widget.attrs = {'class': 'datetime'}
        self.fields['deadline'].widget.attrs = {'class': 'datetime'}
        self.fields['description'].widget.attrs = {
            'class': 'materialize-textarea'
        }
        self.fields['organization'].initial = self.user.unit
        if self.user.unit:
            self.fields['organization'].widget.attrs['readonly'] = True
        self.fields['lowest_year'] = forms.ChoiceField(choices=year_dropdown)
        self.fields['highest_year'] = forms.ChoiceField(
            choices=year_dropdown
        )

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

    def clean_styles(self):
        styles = self.cleaned_data.get('styles')
        return styles.split(',')

    def clean_highest_year(self):
        lowest_year = self.cleaned_data.get('lowest_year')
        highest_year = self.cleaned_data.get('highest_year')
        if lowest_year > highest_year:
            raise forms.ValidationError(
                'Przedział wiekowy jest niepoprawny. '
                'Popraw wartości i spróbuj ponownie.'
            )
        return highest_year

    def save(self, commit=True):
        contest = super(ContestForm, self).save(commit=False)

        contest.content_type = self.user.content_type
        contest.object_id = self.user.object_id
        contest.styles = self.cleaned_data['styles']

        if commit:
            contest.save()
        return contest

    class Meta:
        model = Contest
        fields = [
            'name', 'date', 'place', 'deadline', 'lowest_year',
            'highest_year', 'description',
        ]


class ContestResultsForm(forms.ModelForm):
    """
    Form for add results.
    """

    class Meta:
        model = Contest
        fields = ['results']

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urljoin
from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone

from contest.manager import RushUserManager

UNIT_LIMIT = (
    Q(app_label='contest', model='club') |
    Q(app_label='contest', model='school')
)


class Contact(models.Model):
    """
    Model with contact details.
    """
    email = models.EmailField('adres email')
    website = models.URLField('strona internetowa', blank=True)
    phone_number = models.CharField('numer telefonu', max_length=9, blank=True)

    def __unicode__(self):
        return self.website


class School(models.Model):
    """
    Stores sport clubs data.
    """
    name = models.CharField('nazwa szkoły', max_length=255)
    contact = models.OneToOneField(
        Contact, on_delete=models.CASCADE, null=True,
    )

    def __unicode__(self):
        return self.name


class Club(models.Model):
    """
    Stores sport clubs data.
    """
    name = models.CharField('nazwa klubu', max_length=255)
    code = models.IntegerField('kod klubu', default=0)
    contact = models.OneToOneField(
        Contact, on_delete=models.CASCADE, null=True,
    )

    def __unicode__(self):
        return self.name


class RushUser(AbstractBaseUser, PermissionsMixin):
    """
    User model for Rush users.
    """
    username = models.CharField(
        'nazwa użytkownika', max_length=64, unique=True
    )
    email = models.EmailField('adres email', unique=True)
    first_name = models.CharField('imię', max_length=32)
    last_name = models.CharField('nazwisko', max_length=32)
    organization_name = models.CharField(
        'Nazwa Szkoły/Klubu', max_length=255
    )
    organization_address = models.CharField(
        'Adres Szkoły/Klubu', max_length=255
    )
    date_joined = models.DateTimeField('data dołączenia', auto_now_add=True)
    is_active = models.BooleanField('użytkownik zaakceptowany', default=False)
    is_admin = models.BooleanField(default=False)
    content_type = models.ForeignKey(
        ContentType, limit_choices_to=UNIT_LIMIT, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    unit = GenericForeignKey('content_type', 'object_id')

    objects = RushUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        """
        Return full user name.
        """
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        """
        Return user last name.
        """
        return self.last_name

    def has_perm(self, perm, obj=None):
        """
        Return True if user have specified permission.
        """
        if self.groups.filter(name='Administrators') or self.is_staff:
            return True
        return super(RushUser, self).has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """
        Return True if user have any permission.
        """
        return True

    def set_password(self, raw_password):
        """
        Set password to given by user.
        """
        self.password = make_password(raw_password)

    @property
    def is_staff(self):
        """
        Return True if user has admin privileges.
        """
        return self.is_admin

    @property
    def is_creator(self):
        """
        Return True if user has permission to add contests.
        """
        return self.has_perm('contest.add_contest')

    def get_unit_name(self):
        """
        Return name of user's unit.
        """
        return self.unit.name
    get_unit_name.short_description = 'Szkoła/Klub'
    unit_name = property(get_unit_name)

    def activate(self):
        """
        Activates a user.
        """
        self.is_active = True
        self.save()

    def discard(self):
        """
        Discards an account request.
        """
        self.delete()

    def send_reset_password_email(self, request, initialization=False):
        """
        Sends an email with a link to reset password.
        """
        url_type = 'contest:{}'.format(
            'set-password' if initialization else 'reset-password'
        )
        reset_url = urljoin(
            'http://{}'.format(request.get_host()),
            reverse(
                url_type,
                kwargs={
                    'uidb64': urlsafe_base64_encode(force_bytes(self.pk)),
                    'token': default_token_generator.make_token(self)
                }
            )
        )
        context = {
            'user': self.get_full_name(),
            'url': reset_url,
        }
        template = (
            'email/password_set_email.html' if initialization else
            'email/password_reset_email.html'
        )
        subject = 'Rush - {} hasła'.format(
            'ustawienie' if initialization else 'resetowanie'
        )
        text = loader.render_to_string(template, context)
        msg = EmailMessage(subject, text, 'email_from@rush.pl', [self.email])
        msg.content_subtype = 'html'
        msg.send()


class Contest(models.Model):
    """
    Model for Contest.
    """
    year_dropdown = []
    for x in range(datetime.now().year - 40, (datetime.now().year + 1)):
        year_dropdown.append((x, x))

    name = models.CharField('Nazwa zawodów', max_length=255)
    date = models.DateTimeField('Data')
    place = models.CharField('Miejsce', max_length=255)
    lowest_year = models.IntegerField('Rocznik minimalny', choices=year_dropdown)
    highest_year = models.IntegerField('Rocznik maksymalny', choices=year_dropdown)
    deadline = models.DateTimeField('Termin zgłaszania zawodników')
    description = models.TextField('Opis', blank=True)
    content_type = models.ForeignKey(
        ContentType, limit_choices_to=UNIT_LIMIT,
        blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    organizer = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name or (
            '{} - {}'.format(self.place, self.date.strftime('%d-%m-%Y'))
        )

    @property
    def is_submitting_open(self):
        """
        Return whether a contestant can submit to contest or not.
        """
        return self.deadline > timezone.now()

    @property
    def is_future(self):
        """
        Return whether a contest is a future contest
        or it has already taken place.
        """
        return self.date >= timezone.now()


class Contestant(models.Model):
    """
    Model for Rush Contestant.
    """
    GENDERS = ((None, 'Wybierz płeć'), ('F', 'Kobieta'), ('M', 'Mężczyzna'))
    SCHOOLS = (
        (None, 'Wybierz rodzaj szkoły'),
        ('P', 'Szkoła podstawowa'),
        ('G', 'Gimnazjum'),
        ('S', 'Szkoła średnia'),
    )
    year_dropdown = []
    for x in range(datetime.now().year - 40, (datetime.now().year + 1)):
        year_dropdown.append((x, x))

    moderator = models.ForeignKey(RushUser)
    first_name = models.CharField('imię', max_length=32)
    last_name = models.CharField('nazwisko', max_length=32)
    gender = models.CharField('płeć', max_length=1, choices=GENDERS)
    age = models.IntegerField('Rocznik', choices=year_dropdown)
    school = models.CharField('rodzaj szkoły', max_length=1, choices=SCHOOLS)
    styles_distances = models.CharField('style i dystanse', max_length=255)
    contest = models.ForeignKey(Contest)

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)

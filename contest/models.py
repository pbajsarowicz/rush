# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urljoin

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
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from multiselectfield import MultiSelectField

from contest.manager import RushUserManager
from contest.utils import admin_utils

UNIT_LIMIT = (
    Q(app_label='contest', model='club') |
    Q(app_label='contest', model='school')
)

STYLES_DISTANCES = (
    ('D25', 'Dowolny 25m'), ('D50', 'Dowolny 50m'),
    ('D100', 'Dowolny 100m'), ('D200', 'Dowolny 200m'),
    ('D400', 'Dowolny 400m'), ('D800', 'Dowolny 800m'),
    ('D1500', 'Dowolny 1500m'), ('G25', 'Grzbietowy 25m'),
    ('G50', 'Grzbietowy 50m'), ('G100', 'Grzbietowy 100m'),
    ('G200', 'Grzbietowy 200m'), ('K25', 'Klasyczny 25m'),
    ('K50', 'Klasyczny 50m'), ('K100', 'Klasyczny 100m'),
    ('K200', 'Klasyczny 200m'), ('M25', 'Motylkowy 25m'),
    ('M50', 'Motylkowy 50m'), ('M100', 'Motylkowy 100m'),
    ('M200', 'Motylkowy 200m'), ('Z100', 'Zmienny 100m'),
    ('Z200', 'Zmienny 200m')
)


class UnitModelsMixin(object):

    def unit_name_select(self):
        """
        Returns organizations' names for purposes of admin panel.
        """
        school_options = admin_utils.get_options(
            School, 'Szkoła', self.object_id, self.content_type
        )
        club_options = admin_utils.get_options(
            Club, 'Klub', self.object_id, self.content_type
        )

        return format_html(
            '<select id="id_unit" name="unit">{}{}</select>'.format(
                '<br>'.join(school_options),
                '<br>'.join(club_options)
            )
        )
    unit_name_select.short_description = 'Szkoła/Klub'
    unit_name_select = property(unit_name_select)


class Contact(models.Model):
    """
    Model with contact details.
    """
    email = models.EmailField('adres email')
    website = models.URLField('strona internetowa', blank=True)
    phone_number = models.CharField('numer telefonu', max_length=9, blank=True)

    def __unicode__(self):
        return '{} {} {}'.format(self.email, self.website, self.phone_number)


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


class RushUser(UnitModelsMixin, PermissionsMixin, AbstractBaseUser):
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

    @property
    def unit_name(self):
        """
        Return name of user's unit.
        """
        return self.unit.name

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


class Contest(UnitModelsMixin, models.Model):
    """
    Model for Contest.
    """

    name = models.CharField('Nazwa zawodów', max_length=255)
    date = models.DateTimeField('Data')
    place = models.CharField('Miejsce', max_length=255)
    lowest_year = models.PositiveSmallIntegerField('Rocznik minimalny')
    highest_year = models.PositiveSmallIntegerField('Rocznik maksymalny')
    deadline = models.DateTimeField('Termin zgłaszania zawodników')
    description = models.TextField('Opis', blank=True)
    results = models.TextField('Wyniki', blank=True)
    content_type = models.ForeignKey(
        ContentType, limit_choices_to=UNIT_LIMIT,
        blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    organizer = GenericForeignKey('content_type', 'object_id')
    styles = MultiSelectField(choices=STYLES_DISTANCES)

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

    moderator = models.ForeignKey(RushUser)
    first_name = models.CharField('imię', max_length=32)
    last_name = models.CharField('nazwisko', max_length=32)
    gender = models.CharField('płeć', max_length=1, choices=GENDERS)
    year_of_birth = models.PositiveSmallIntegerField('Rocznik')
    school = models.CharField('rodzaj szkoły', max_length=1, choices=SCHOOLS)
    styles = MultiSelectField(choices=STYLES_DISTANCES)
    contest = models.ForeignKey(Contest)

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)

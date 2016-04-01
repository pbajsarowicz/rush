# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urljoin
from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from unidecode import unidecode

from contest.manager import RushUserManager


class Club(models.Model):
    """
    Stores sport clubs data.
    """
    name = models.CharField('nazwa klubu', max_length=255)
    code = models.IntegerField('kod klubu', default=0)

    def __unicode__(self):
        return self.name


class RushUser(AbstractBaseUser):
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
        'nazwa organizacji', blank=True, max_length=255
    )
    organization_address = models.CharField(
        'adres organizacji', max_length=255
    )
    date_joined = models.DateTimeField('data dołączenia', auto_now_add=True)
    is_active = models.BooleanField('użytkownik zaakceptowany', default=False)
    is_admin = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    club = models.ForeignKey(Club, blank=True, null=True)

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
        return True

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

    def _get_username(self):
        """
        Returns username for an active user.
        """
        return unidecode(
            '{}{}'.format(self.first_name[0], self.last_name)
        ).lower()

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

    def send_reset_email(self, request):
        """
        Sends an email with a link to reset password.
        """
        reset_url = urljoin(
            'http://{}'.format(request.get_host()),
            reverse(
                'contest:set-password',
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
        text = loader.render_to_string(
            'email/password_reset_email.html', context
        )
        msg = EmailMessage(
            'Rush - ustawienie hasła',
            text,
            'email_from@rush.pl',
            [self.email],
        )
        msg.content_subtype = 'html'
        msg.send()


class Organizer(models.Model):
    """
    Model for contest organizer.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    phone_number = models.CharField(max_length=9, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    club = models.OneToOneField(Club)

    def __unicode__(self):
        return self.name


class Contest(models.Model):
    """
    Model for Contest.
    """
    organizer = models.ForeignKey(Organizer)
    date = models.DateTimeField()
    place = models.CharField(max_length=255)
    age_min = models.SmallIntegerField()
    age_max = models.SmallIntegerField()
    deadline = models.DateTimeField()
    description = models.TextField(blank=True)

    def __unicode__(self):
        return '{} {}'.format(
            self.place, datetime.strftime(self.date, '%d.%m.%Y %X')
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
    moderator = models.ForeignKey(RushUser)
    first_name = models.CharField('imię', max_length=32)
    last_name = models.CharField('nazwisko', max_length=32)
    gender = models.CharField('płeć', max_length=1, choices=GENDERS)
    age = models.IntegerField('wiek')
    school = models.CharField('rodzaj szkoły', max_length=255)
    styles_distances = models.CharField('style i dystanse', max_length=255)
    contest = models.ForeignKey(Contest)

    def __unicode__(self):
        return '{} {}'.format(self.first_name, self.last_name)

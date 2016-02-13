# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urljoin
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from unidecode import unidecode

from contest.manager import RushUserManager
from contest.utils import is_uuid4


class Club(models.Model):
    """
    Stores sport clubs data
    """
    name = models.CharField('nazwa klubu', max_length=255)
    code = models.IntegerField('kod klubu', default=0)

    def __unicode__(self):
        return str(self.code)


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
        Initialize password with empty string.
        """
        self.password = (
            make_password(raw_password) if self.is_admin or self.is_active
            else ''
        )
        self._password = (
            raw_password if self.is_admin or self.is_active else ''
        )

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

    def _initialize_username(self):
        """
        Initialize username:
        * with the value given by hand (shell),
        * with the uuid4 value, when somebody asks for an account,
        * with the value consistent with pattern `first letter
          of firstname + lastname` when an admin accepts an account.
        """
        if self.is_active:
            self.username = (
                self.username if self.username and not is_uuid4(self.username)
                else self._get_username()
            )
        else:
            self.username = self.username if self.username else uuid.uuid4()

    def save(self, *args, **kwargs):
        """
        Provide extra RushUser's logic
        """
        self._initialize_username()

        return super(RushUser, self).save(*args, **kwargs)

    def activate(self):
        """
        Activates a user and sets a password.
        """
        self.is_active = True
        self.set_password('password123')
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
            'username': self.username,
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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from unidecode import unidecode

from contest.manager import RushUserManager
from contest.utils import is_uuid4


class RushUser(AbstractBaseUser):
    """
    User model for Rush users.
    """

    username = models.CharField(
        'Nazwa użytkownika', max_length=64, unique=True
    )
    email = models.EmailField('Adres email', blank=False, unique=True)
    first_name = models.CharField('Imię', max_length=32, blank=False)
    last_name = models.CharField('Nazwisko', max_length=32, blank=False)
    organization_name = models.CharField(
        'Nazwa organizacji', max_length=255, blank=False
    )
    organization_address = models.CharField(
        'Adres organizacji', max_length=255, blank=False
    )
    date_joined = models.DateTimeField('Data dołączenia', auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

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
        self.password = raw_password if self.is_admin else ''
        self._password = raw_password if self.is_admin else ''

    def _get_username(self):
        """
        Returns username for active a user.
        """
        return unidecode(
            '{}{}'.format(self.first_name[0], self.last_name)
        ).lower()

    def create(self, request, queryset):
        """
        Creating an account (set login, temporary password, active status)
        """
        for user in queryset:
            user.is_active = True
            user.set_password('password123')
            user.save()

    def save(self, *args, **kwargs):
        """
        Initialize username.
        """
        if self.is_active:
            self.username = (
                self.username if self.username and not is_uuid4(self.username)
                else self._get_username()
            )
        else:
            self.username = self.username if self.username else uuid.uuid4()

        return super(RushUser, self).save(*args, **kwargs)

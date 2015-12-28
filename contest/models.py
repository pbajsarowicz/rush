# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

from contest.manager import RushUserManager

import uuid


class RushUser(AbstractBaseUser):
    """
    User model for Rush users.
    """
    login=models.CharField(
            'Login użytkownika', max_length=30,
            unique=True
        )
    email=models.EmailField(
            'Adres email', blank=False,
            unique=True
        )
    first_name=models.CharField (
            'Imię', max_length=30, blank=False
        )
    last_name=models.CharField (
            'Nazwisko', max_length=30, blank=False
        )
    organization_name=models.CharField (
            'Nazwa organizacji', max_length=30, blank=False
        )
    organization_address=models.CharField (
            'Adres organizacji', max_length=30, blank=False
        )
    date_joined=models.DateTimeField('Data dołączenia',
        auto_now_add=True
        )
    is_active=models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)

    objects=RushUserManager()

    USERNAME_FIELD = 'login'

    def __unicode__(self):
        return self.email

    def full_name(self):
        """
        Return full user name.
        """
        return '{} {}'.format(self.first_name, self.last_name)

    def get_full_name(self):
        """
        Return user first name, last name and email address.
        """
        return self.email

    def get_short_name(self):
        """
        Return user email address.
        """
        return self.email

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

    def save(self, *args, **kwargs):
        """
        Initialize login with unique value.
        """
        self.login=uuid.uuid4()
        return super(RushUser, self).save(*args, **kwargs)

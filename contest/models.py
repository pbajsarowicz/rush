# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from contest.manager import RushUserManager


class RushUser(AbstractBaseUser):

    email = models.EmailField('adres email', unique=True, db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField('imie', max_length=30, null=True)
    last_name = models.CharField('nazwisko', max_length=30, null=True)
    organization_name = models.CharField('nazwa organizacji',
                                         max_length=30, null=True)
    organization_address = models.CharField('adres organizacji',
                                            max_length=30, null=True)
    is_active = models.BooleanField(default=False)

    objects = RushUserManager()
    USERNAME_FIELD = 'email'

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def is_staff(self):
        return self.is_admin

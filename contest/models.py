from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import AbstractBaseUser

from django.utils import timezone


class User(AbstractBaseUser):

    email = models.EmailField('adres email', unique = True, db_index = True)
    joined = models.DateTimeField(auto_now_add = True)
    first_name = models.CharField ('imie',max_length = 30, null = True)
    last_name = models.CharField ('nazwisko',max_length = 30, null = True)
    organization_name = models.CharField ('nazwa organizacji', 
    										max_length = 30, null = True)
    organization_address = models.CharField ('adres organizacji',
    											max_length = 30, null = True)

    USERNAME_FIELD = 'email'


    def __unicode__(self):
        return self.email
 
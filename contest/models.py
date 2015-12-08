from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):

    email = models.EmailField('email address', unique=True, db_index=True)
    joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField (max_length = 30, null = True)
    last_name = models.CharField (max_length = 30, null = True)
    organization_name = models.CharField (max_length = 30, null = True)
    organization_address = models.CharField (max_length = 30, null = True)

    USERNAME_FIELD = 'email'

    def __unicode__(self):
        return self.email

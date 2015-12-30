# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class RushUserManager(BaseUserManager):
    """
    Manager for RushUser creation.

    """

    def create_user(
            self, email, username='', password='', first_name='',
            last_name='', organization_name='',
            organization_address=''
    ):
        """
        Regular user creation.
        """
        try:
            email = self.normalize_email(email)
        except ValueError as error:
            raise error('Podaj poprawny adres email')
        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name,
            organization_address=organization_address,
            date_joined=timezone.now()
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email):
        """
        Super user creation.
        """

        user = self.create_user(
            email=email, username=username, password=password
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)

        return user

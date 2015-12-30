# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import BaseUserManager


class RushUserManager(BaseUserManager):
    """
    Manager for RushUser creation.
    """
    def create_user(
        self, username='', password='', email='', first_name='', last_name='',
        organization_name='', organization_address=''
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
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email):
        """
        Superuser creation.
        """

        user = self.create_user(
            username=username, password=password, email=email
        )
        user.is_admin = True
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)

        return user

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.contrib.auth.models import BaseUserManager


class RushUserManager(BaseUserManager):
    """
    Manager for RushUser creation.
    """
    def create_user(
        self, email, username='', password='', first_name='', last_name='',
        organization_name='', organization_address=''
    ):
        """
        Regular user creation.
        """

        email = self.normalize_email(email)
        user = self.model(
            username=username if username else uuid.uuid4(),
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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.models import ContentType


class RushUserManager(BaseUserManager):
    """
    Manager for RushUser creation.
    """
    def create_user(
        self, email, username='', password='', first_name='', last_name='',
        organization_name='', organization_address='', is_active=False,
        is_admin=False, unit=None
    ):
        """
        Regular user creation.
        """
        email = self.normalize_email(email)

        fields = {
            'username': username if username else uuid.uuid4(),
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'organization_name': organization_name,
            'organization_address': organization_address,
            'is_active': is_active,
            'is_admin': is_admin
        }

        if unit:
            fields.update({
                'content_type': ContentType.objects.get_for_model(unit),
                'object_id': unit.pk,
            })

        user = self.model(**fields)

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

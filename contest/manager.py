# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import BaseUserManager


class RushUserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, organization_name,
                    organization_address, password):

        if not email:
            raise ValueError('Podaj poprawny adres email')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name,
            organization_address=organization_address,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

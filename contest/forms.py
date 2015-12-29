# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from contest.models import RushUser


class RegistrationForm(forms.ModelForm):
    """
    Form for new user registration.
    """

    class Meta:
        model = RushUser
        fields = [
            'email', 'first_name', 'last_name', 'organization_name',
            'organization_address',
        ]

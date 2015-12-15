# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import authenticate

from contest.models import RushUser
from contest.forms import LoginForm


class UserMethodTests(TestCase):
    def setUp(self):
        self.user = RushUser.objects.create_user(
            'xyz@xyz.pl', 'Name', 'Last Name', 'School', 'Address', 'Password'
        )

    def test_authenticate(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.

        """

        self.assertEqual(
            authenticate(
                email='xyz@xyz.pl',
                password='Password'),
            self.user
        )
        self.assertEqual(
            authenticate(
                email='xyz@xyz.pl',
                password='random_pass'),
            None
        )
        self.assertEqual(
            authenticate(
                email='example@example.pl',
                password='qwerty'),
            None
        )
        self.assertEqual(authenticate(email='', password=''), None)

    def test_login_form(self):
        """
        Checking if form is valid for correct data and invalid for
        wrong data or inactive user
        """
        self.assertEqual(list(LoginForm.base_fields), ['username', 'password'])

        form_data = {'username': 'xyz@xyz.pl', 'password': 'wrong_password'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            [
                'Wprowadź poprawny adres email oraz hasło. '
                'Uwaga: wielkość liter ma znaczenie.'
            ]
        )

        form_data = {'username': 'xyz@xyz.pl', 'password': 'Password'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            [
                'Konto nie zostało aktywowane'
            ]
        )

        self.user.is_active = True
        self.user.save()
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import authenticate
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from contest.models import RushUser
from contest.forms import LoginForm
from contest.admin import RushUserAdmin


class UserMethodTests(TestCase):
    def setUp(self):
        self.user = RushUser.objects.create_user(
            'xyz@xyz.pl', 'Name', 'Last Name', 'School', 'Address', 'Password',
            'username'
        )

    def test_authenticate(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.
        """
        self.assertEqual(
            authenticate(username='username', password='Password'),
            self.user
        )
        self.assertEqual(
            authenticate(username='username', password='random_pass'),
            None
        )
        self.assertEqual(
            authenticate(username='example@example.pl', password='qwerty'),
            None
        )
        self.assertEqual(authenticate(username='', password=''), None)

    def test_login_form(self):
        """
        Checking if form is valid for correct data and invalid for
        wrong data or inactive user
        """
        self.assertEqual(list(LoginForm.base_fields), ['username', 'password'])

        form_data = {'username': 'username', 'password': 'wrong_password'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            [
                'Wprowadź poprawny login oraz hasło. '
                'Uwaga: wielkość liter ma znaczenie.'
            ]
        )

        form_data = {'username': 'username', 'password': 'Password'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'], ['Konto nie zostało aktywowane']
        )

        self.user.is_active = True
        self.user.save()
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())


class AdminMethodTests(TestCase):
    def setUp(self):
        self.obj_1 = RushUser.objects.create_user(
            'aaa@aaa.pl', 'Łukasz', 'Ślązak', 'School', 'Address', 'Password',
            'login1'
        )
        self.obj_2 = RushUser.objects.create_user(
            'bbb@bbb.pl', 'Adam', 'Ślowacki', 'School', 'Address', 'Password',
            'login2'
        )
        self.obj_3 = RushUser.objects.create_user(
            'ccc@ccc.pl', 'Ewa', 'Kowalska', 'School', 'Address', 'Password',
            'random_login'
        )

        self.request = HttpRequest()
        self.app_admin = RushUserAdmin(RushUser, AdminSite())

    def test_creating_user(self):
        self.assertFalse(self.obj_1.is_active and self.obj_2.is_active)
        self.assertEqual(self.obj_1.username, 'login1')
        self.assertEqual(self.obj_2.username, 'login2')

        queryset = [self.obj_1, self.obj_2]
        self.app_admin.create(self.request, queryset)

        self.assertTrue(self.obj_1.is_active and self.obj_2.is_active)
        self.assertEqual(self.obj_1.username, 'lslazak')
        self.assertEqual(self.obj_2.username, 'aslowacki')

    def test_deleting_user(self):
        self.assertTrue(RushUser.objects.filter(email='ccc@ccc.pl'))

        queryset = RushUser.objects.filter(email='ccc@ccc.pl')
        self.app_admin.cancel(self.request, queryset)

        self.assertFalse(RushUser.objects.filter(email='ccc@ccc.pl'))

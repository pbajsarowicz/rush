# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.test import TestCase
from django.contrib.auth import authenticate
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.core.urlresolvers import reverse

from contest.models import RushUser
from contest.forms import LoginForm, SettingPasswordForm
from contest.admin import RushUserAdmin


class UserMethodTests(TestCase):
    def setUp(self):
        self.user = RushUser.objects.create_user(
            email='xyz@xyz.pl', first_name='Name', last_name='Last Name',
            organization_name='School', organization_address='Address',
            password='Password', username='username'
        )
        RushUser.objects.create_user(
            email='test@xyz.pl', first_name='Name',
            last_name='Last Name', organization_name='Org',
            organization_address='Address'
        )
        RushUser.objects.create_superuser(
            email='testsuper@cos.pl', username='test',
            password='P@ssw0rd'
        )

    def test_user(self):
        """
        Checking status and informations for user.
        """
        user_test = RushUser.objects.get(email='test@xyz.pl')
        self.assertEqual(user_test.email, 'test@xyz.pl')
        self.assertEqual(user_test.first_name, 'Name')
        self.assertEqual(user_test.last_name, 'Last Name')
        self.assertEqual(user_test.organization_name, 'Org')
        self.assertEqual(user_test.organization_address, 'Address')
        self.assertFalse(user_test.is_active)
        self.assertFalse(user_test.is_admin)

    def test_superuser(self):
        """
        Checking status and informations for super user.
        """
        superuser_test = RushUser.objects.get(email='testsuper@cos.pl')
        self.assertTrue(superuser_test.is_active)
        self.assertTrue(superuser_test.is_admin)

    def test_authenticate(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.
        """
        self.user.is_active = True
        self.user.set_password('Password')
        self.user.save()

        self.assertEqual(
            authenticate(username='username', password='Password'),
            self.user
        )
        self.assertIsNone(
            authenticate(username='username', password='random_pass')
        )
        self.assertIsNone(
            authenticate(username='example@example.pl', password='qwerty')
        )
        self.assertIsNone(authenticate(username='', password=''))

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
        self.user.is_active = True
        self.user.set_password('Password')
        self.user.save()
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())


class AdminMethodTests(TestCase):
    def setUp(self):
        self.initial_user1_username = str(uuid.uuid4())
        self.initial_user_2_username = str(uuid.uuid4())

        self.user_1 = RushUser.objects.create_user(
            email='aaa@aaa.pl', first_name='Łukasz', last_name='Ślązak',
            organization_name='School', organization_address='Address',
            password='Password', username=self.initial_user1_username
        )
        self.user_2 = RushUser.objects.create_user(
            email='bbb@bbb.pl', first_name='Adam', last_name='Ślowacki',
            organization_name='School', organization_address='Address',
            password='Password', username=self.initial_user_2_username
        )
        self.user_3 = RushUser.objects.create_user(
            email='ccc@ccc.pl', first_name='Ewa', last_name='Kowalska',
            organization_name='School', organization_address='Address',
            password='Password', username='random_login'
        )

        self.request = HttpRequest()
        self.app_admin = RushUserAdmin(RushUser, AdminSite())

    def test_creating_user(self):
        self.assertFalse(self.user_1.is_active and self.user_2.is_active)
        self.assertEqual(self.user_1.username, self.initial_user1_username)
        self.assertEqual(self.user_2.username, self.initial_user_2_username)

        queryset = [self.user_1, self.user_2]
        self.app_admin.create(self.request, queryset)

        self.assertTrue(self.user_1.is_active and self.user_2.is_active)
        self.assertEqual(self.user_1.username, 'lslazak')
        self.assertEqual(self.user_2.username, 'aslowacki')

    def test_deleting_user(self):
        queryset = RushUser.objects.filter(email='ccc@ccc.pl')
        self.assertTrue(queryset.exists())
        self.app_admin.cancel(self.request, queryset)
        self.assertFalse(queryset.exists())


class PasswordSettingTests(TestCase):
    def setUp(self):
        self.user_1 = RushUser(
            email='ddd@ddd.pl', first_name='Łukasz', last_name='Ślązak',
            is_active=True
        )
        self.user_1.set_password('password123')
        self.user_1.save()

        self.user_2 = RushUser(
            email='kkk@kkk.pl', first_name='Ewa', last_name='Olczak',
            is_active=True
        )
        self.user_2.set_password('Password_already_set')
        self.user_2.save()

    def test_correct_url(self):
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'user': 'lslazak'}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], SettingPasswordForm)
        )

        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'user': 'eolczak'}
            )
        )
        expected_message = 'Użytkownik już ma ustawione hasło!'
        self.assertEqual(response.context['message'], expected_message)

        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'user': 'invalidlogin'}
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_setting_password(self):
        form_data = {'new_password1': 'pass1234', 'new_password2': 'sad_panda'}
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={'user': 'lslazak'}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        expected_message = 'Hasła nie są identyczne.'
        self.assertContains(response, expected_message)

        form_data = {'new_password1': 'pass1234', 'new_password2': 'pass1234'}
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={'user': 'lslazak'}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        expected_message = 'Hasło ustawione, można się zalogować.'
        self.assertEqual(response.context['message'], expected_message)

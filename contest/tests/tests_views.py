# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from contest.forms import (
    LoginForm,
    RegistrationForm,
    SettingPasswordForm,
)
from contest.models import RushUser
from contest.views import SetPasswordView


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = RushUser.objects.create_user(
            email='xyz@xyz.pl', first_name='Name', last_name='LastName',
            organization_name='School', organization_address='Address',
            username='username'
        )
        self.user.is_active = True
        self.user.set_password('Password')
        self.user.save()

    def test_authenticate(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.
        """
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

    def test_login_view(self):
        """
        Checking if form is valid for correct data and invalid for
        wrong data or inactive user
        """
        response = self.client.get(reverse('contest:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], LoginForm)
        )
        self.assertEqual(list(LoginForm.base_fields), ['username', 'password'])

        form_data = {'username': 'username', 'password': 'wrong_password'}
        response = self.client.post(reverse('contest:login'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['__all__'],
            [
                'Wprowadź poprawny login oraz hasło. '
                'Uwaga: wielkość liter ma znaczenie.'
            ]
        )

        form_data = {'username': 'username', 'password': 'Password'}
        response = self.client.post(reverse('contest:login'), data=form_data)
        self.assertEqual(response.status_code, 302)


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
            is_active=True, username='username_taken'
        )
        self.user_2.set_password('Password_already_set')
        self.user_2.save()
        self.user1_uid = urlsafe_base64_encode(force_bytes(self.user_1.pk))
        self.user1_token = default_token_generator.make_token(self.user_1)

    def test_correct_url(self):
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], SettingPasswordForm)
        )

        wrong_token = default_token_generator.make_token(self.user_2)
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': wrong_token}
            )
        )
        self.assertEqual(response.status_code, 302)

        wrong_uid = urlsafe_base64_encode(force_bytes(self.user_2.pk))
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': wrong_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SetPasswordView._get_user('00'))

    def test_setting_password(self):
        form_data = {
            'new_password1': 'pass1234', 'new_password2': 'sad_panda',
            'username': 'username_taken'
        }
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'username': ['Podana nazwa użytkownika jest już zajęta.'],
                'new_password2': ['Hasła nie są identyczne.']
            }
        )

        form_data = {
            'new_password1': 'pass1234', 'new_password2': 'pass1234',
            'username': 'username123'
        }
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Hasło ustawione, można się zalogować.'
        )


class AccountsViewTestCase(TestCase):
    def setUp(self):
        user = RushUser(
            email='auth@user.pl', first_name='auth', last_name='auth',
            is_active=True, username='auth'
        )
        user.set_password('password123')
        user.save()

        self.client.login(username='auth', password='password123')

    def test_get(self):
        inactive_user = RushUser.objects.create(
            email='inactive_user@user.pl', first_name='Test',
            last_name='Anonymous', is_active=False, username='inactive_user'
        )

        response = self.client.get(reverse('contest:accounts'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0], inactive_user)

    def test_post(self):
        user = RushUser(
            email='test@user.pl', first_name='Test', last_name='Anonymous',
            is_active=False
        )
        user.set_password('password123')
        user.save()

        response = self.client.post(
            reverse('contest:accounts', kwargs={'user_id': user.id})
        )

        user = RushUser.objects.get(pk=user.id)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(user.is_active)

        response = self.client.post(
            reverse('contest:accounts', kwargs={'user_id': 0})
        )
        self.assertEqual(response.status_code, 500)

    def test_delete(self):
        user = RushUser(
            email='test@user.pl', first_name='Test', last_name='Anonymous',
            is_active=False
        )
        user.set_password('password123')
        user.save()

        response = self.client.delete(
            reverse('contest:accounts', kwargs={'user_id': user.id})
        )
        self.assertFalse(RushUser.objects.filter(pk=user.id).exists())
        self.assertEqual(response.status_code, 204)

        response = self.client.delete(
            reverse('contest:accounts', kwargs={'user_id': user.id})
        )
        self.assertEqual(response.status_code, 500)


class RegisterViewTests(TestCase):
    def test_register_view(self):
        response = self.client.get(reverse('contest:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], RegistrationForm)
        )

        response = self.client.post(reverse('contest:register'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'first_name': ['To pole jest wymagane.'],
                'last_name': ['To pole jest wymagane.'],
                'organization_address': ['To pole jest wymagane.'],
                'email': ['To pole jest wymagane.']
            }
        )

        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'abc@tmp.com', 'first_name': 'Imie',
                'last_name': 'Nazwisko', 'organization_name': 'School',
                'organization_address': 'Address'
            }
        )
        self.assertEqual(response.context['email'], settings.SUPPORT_EMAIL)

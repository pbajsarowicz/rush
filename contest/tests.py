# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.test import TestCase
from django.contrib.auth import authenticate
from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.http import HttpRequest

from contest.models import RushUser
from contest.forms import LoginForm, SettingPasswordForm
from contest.admin import RushUserAdmin


class UserMethodTests(TestCase):
    def setUp(self):
        self.user = RushUser.objects.create_user(
            email='xyz@xyz.pl', first_name='Name', last_name='LastName',
            organization_name='School', organization_address='Address',
            username='username'
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
        self.user.is_active = True
        self.user.set_password('Password')
        self.user.save()

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
        self.request.META['SERVER_NAME'] = '127.0.0.1'
        self.request.META['SERVER_PORT'] = '8000'
        self.app_admin = RushUserAdmin(RushUser, AdminSite())
        self.user_3.is_active = True

    def test_creating_user_and_sending_mail(self):
        self.assertFalse(self.user_1.is_active and self.user_2.is_active)
        self.assertEqual(self.user_1.username, self.initial_user1_username)
        self.assertEqual(self.user_2.username, self.initial_user_2_username)

        queryset = [self.user_1, self.user_2, self.user_3]
        self.app_admin.create(self.request, queryset)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.user_1.email])
        uid = urlsafe_base64_encode(force_bytes(self.user_1.pk))
        token = default_token_generator.make_token(self.user_1)
        reset_url = '/set_password/{}/{}/'.format(uid, token)
        self.assertIn(str(reset_url), mail.outbox[0].body)

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

    def test_setting_password(self):
        form_data = {'new_password1': 'pass1234', 'new_password2': 'sad_panda'}
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
            {'new_password2': [u'Hasła nie są identyczne.']}
        )

        form_data = {'new_password1': 'pass1234', 'new_password2': 'pass1234'}
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

        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 302)

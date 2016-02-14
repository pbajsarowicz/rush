# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.http import HttpRequest

from contest.admin import RushUserAdmin
from contest.models import RushUser


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
        self.assertEqual(mail.outbox[1].to, [self.user_2.email])
        uid = urlsafe_base64_encode(force_bytes(self.user_1.pk))
        token = default_token_generator.make_token(self.user_1)
        reset_url = reverse(
            'contest:set-password',
            kwargs={'uidb64': uid, 'token': token}
        )
        self.assertIn(reset_url, mail.outbox[0].body)

        self.assertTrue(self.user_1.is_active and self.user_2.is_active)
        self.assertEqual(self.user_1.username, 'lslazak')
        self.assertEqual(self.user_2.username, 'aslowacki')

    def test_deleting_user(self):
        queryset = RushUser.objects.filter(email='ccc@ccc.pl')
        self.assertTrue(queryset.exists())
        self.app_admin.cancel(self.request, queryset)
        self.assertFalse(queryset.exists())

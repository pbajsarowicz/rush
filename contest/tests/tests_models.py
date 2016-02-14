# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from contest.models import RushUser


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
        self.assertEqual(user_test.get_full_name(), 'Name Last Name')
        self.assertEqual(user_test.get_short_name(), 'Last Name')
        self.assertTrue(user_test.has_perm(None))
        self.assertTrue(user_test.has_module_perms(None))
        self.assertFalse(user_test.is_staff())
        self.assertEqual(user_test.__unicode__(), 'test@xyz.pl')
        user_test.discard()
        self.assertFalse(RushUser.objects.filter(email='test@xyz.pl'))

    def test_superuser(self):
        """
        Checking status and informations for super user.
        """
        superuser_test = RushUser.objects.get(email='testsuper@cos.pl')
        self.assertTrue(superuser_test.is_active)
        self.assertTrue(superuser_test.is_admin)

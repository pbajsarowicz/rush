# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from contest.models import RushUser


class UserMethodTests(TestCase):
	"""
	Test for user creation.
	"""
	def setUp(self):
		"""
		Creating test users.
		"""
		user=RushUser.objects.create_user(
				'test@xyz.pl', 'Name',
				'Last Name', 'Org', 'Address', 'Password'
			)
		superuser=RushUser.objects.create_superuser(
				email='testsuper@cos.pl'
			)

	def test_user(self):
		"""
		Checking status and informations for user.
		"""
		user_test=RushUser.objects.get(email='test@xyz.pl')
		self.assertEqual(user_test.email, 'test@xyz.pl')
		self.assertEqual(user_test.first_name ,'Name')
		self.assertEqual(user_test.last_name ,'Last Name')
		self.assertEqual(user_test.organization_name ,'Org')
		self.assertEqual(user_test.organization_address ,'Address')
		self.assertEqual(user_test.is_active ,False)
		self.assertEqual(user_test.is_admin ,False)

	def test_superuser(self):
		"""
		Checking status and informations for super user.
		"""
		superuser_test=RushUser.objects.get(email='testsuper@cos.pl')
		self.assertEqual(superuser_test.is_active ,True)
		self.assertEqual(superuser_test.is_admin ,True)

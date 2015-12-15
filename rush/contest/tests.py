from django.test import TestCase

from contest.models import RushUser


class UserMethodTests(TestCase):
	def setUp(self):
		q=RushUser.objects.create_user('test@xyz.pl', 'Name', 'Last Name',
			'Org', 'Address', 'Password'
			)
		q.save()

	def test_authenticate(self):
		first=RushUser.objects.get(email='test@xyz.pl')
		self.assertEqual(first.email, 'test@xyz.pl')
		self.assertEqual(first.first_name ,'Name')
		self.assertEqual(first.last_name ,'Last Name')
		self.assertEqual(first.organization_name ,'Org')
		self.assertEqual(first.organization_address ,'Address')

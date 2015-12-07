from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserMethodTests(TestCase):
    def setUp(self):
        User.objects.create(username='xyz@xyz.pl')
        q = User.objects.get(username='xyz@xyz.pl')
        q.set_password('qwerty')
        q.save()

    def test_logging_user(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.
        """
        first = User.objects.get(username='xyz@xyz.pl')
        self.assertEqual(authenticate(username='xyz@xyz.pl',
                                      password='qwerty'),
                         first)
        self.assertEqual(authenticate(username='xyz@xyz.pl',
                                      password='random_pass'),
                         None)
        self.assertEqual(authenticate(username='example@example.pl',
                                      password='qwerty'),
                         None)
        self.assertEqual(authenticate(username='', password=''), None)

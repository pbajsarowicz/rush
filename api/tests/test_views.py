# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase, APIClient

from contest.models import RushUser


class ContestTestsAPI(APITestCase):
    fixtures = [
        'organizers.json', 'contests.json', 'clubs.json',
        'users.json'
    ]

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.get('/api/v1/contests/?format=json')

    def test_getting_info(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(self.response.data['results']), 3)
        self.assertEqual(
            self.response.data['results'][2]['place'],
            'Basen Wodnik w Pile'
        )
        self.assertEqual(
            self.response.data['results'][1]['place'],
            'Basen Wodnik w Poznaniu'
        )
        self.assertEqual(
            self.response.data['results'][0]['organizer']['website'],
            'http://www.google.pl'
        )


class ContestantTestsAPI(APITestCase):
    fixtures = [
        'contestants.json', 'organizers.json', 'contests.json', 'clubs.json',
        'users.json'
    ]

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.get('/api/v1/contestants/?format=json')
        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        self.response_2 = self.client.get('/api/v1/contestants/?format=json')

    def test_getting_info(self):
        self.assertEqual(
            self.response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )
        self.assertEqual(len(self.response_2.data['results']), 4)


class ClubTestsAPI(APITestCase):
    fixtures = ['clubs.json']

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.get('/api/v1/clubs/?format=json')
        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        self.response_2 = self.client.get('/api/v1/clubs/?format=json')

    def test_getting_info(self):
        self.assertEqual(
            self.response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )
        self.assertEqual(len(self.response_2.data['results']), 2)


class OrganizerTestsAPI(APITestCase):
    fixtures = ['organizers.json', 'clubs.json']

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.get('/api/v1/organizers/?format=json')
        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        self.response_2 = self.client.get('/api/v1/organizers/?format=json')

    def test_getting_info(self):
        self.assertEqual(
            self.response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )
        self.assertEqual(len(self.response_2.data['results']), 2)


class UserTestsAPI(APITestCase):
    fixtures = ['clubs.json', 'users.json']

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.get('/api/v1/users/?format=json')
        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        self.response_2 = self.client.get('/api/v1/users/?format=json')

    def test_getting_info(self):
        self.assertEqual(
            self.response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )
        self.assertEqual(len(self.response_2.data['results']), 3)

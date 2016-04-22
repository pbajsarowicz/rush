# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse

from rest_framework.test import (
    APITestCase,
    APIClient,
)

from contest.models import RushUser


class ContactTestsAPI(APITestCase):
    fixtures = ['contact.json']

    def setUp(self):
        self.client = APIClient()
        url = reverse('contest:contact-list')
        self.response = self.client.get(url)
        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        self.response_2 = self.client.get(url)

    def test_getting_info(self):
        self.assertEqual(
            self.response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )
        self.assertEqual(len(self.response_2.data['results']), 2)


class ContestTestsAPI(APITestCase):
    fixtures = [
        'contest/fixtures/organizers.json',
        'contest/fixtures/contests.json',
        'contest/fixtures/clubs.json',
        'contest/fixtures/users.json',
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
        self.assertEqual(self.response.data['results'][0]['age_min'], 10)
        self.assertEqual(self.response.data['results'][0]['age_max'], 20)


class ContestantTestsAPI(APITestCase):
    fixtures = [
        'contest/fixtures/contestants.json',
        'contest/fixtures/organizers.json',
        'contest/fixtures/contests.json',
        'contest/fixtures/clubs.json',
        'contest/fixtures/users.json',
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
    fixtures = ['contest/fixtures/clubs.json']

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


class SchoolTestsAPI(APITestCase):
    fixtures = ['schools.json']

    def setUp(self):
        self.client = APIClient()
        self.response = self.client.get('/api/v1/schools/?format=json')
        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        self.response_2 = self.client.get('/api/v1/schools/?format=json')

    def test_getting_info(self):
        self.assertEqual(
            self.response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )
        self.assertEqual(len(self.response_2.data['results']), 2)


class UserTestsAPI(APITestCase):
    fixtures = [
        'contest/fixtures/clubs.json',
        'contest/fixtures/users.json'
    ]

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

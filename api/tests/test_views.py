# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse

from rest_framework.test import (
    APITestCase,
    APIClient,
)

from contest.models import RushUser


class ApiTestCasesMixin(object):

    def setUp(self):
        self.client = APIClient()


class ContactTestsAPI(ApiTestCasesMixin, APITestCase):
    fixtures = ['contact.json']

    def test_getting_info(self):
        url = reverse('api:contact-list')
        response = self.client.get(url)
        self.assertEqual(
            response.data['detail'], 'Nie podano danych uwierzytelniających.'
        )

        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        response = self.client.get(url)

        self.assertEqual(len(response.data['results']), 2)


class ContestTestsAPI(ApiTestCasesMixin, APITestCase):
    fixtures = [
        'contest/fixtures/contests.json',
        'contest/fixtures/clubs.json',
        'contest/fixtures/users.json',
    ]

    def test_getting_info(self):
        response = self.client.get(reverse('api:contest-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(
            response.data['results'][2]['place'],
            'Basen Wodnik w Pile'
        )
        self.assertEqual(
            response.data['results'][1]['place'],
            'Basen Wodnik w Poznaniu'
        )
        self.assertEqual(response.data['results'][0]['age_min'], 10)
        self.assertEqual(response.data['results'][0]['age_max'], 20)


class ContestantTestsAPI(ApiTestCasesMixin, APITestCase):
    fixtures = [
        'contest/fixtures/contestants.json',
        'contest/fixtures/contests.json',
        'contest/fixtures/clubs.json',
        'contest/fixtures/users.json',
    ]

    def test_getting_info(self):
        response = self.client.get(reverse('api:contestant-list'))
        self.assertEqual(
            response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )

        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('api:contestant-list'))
        self.assertEqual(len(response.data['results']), 4)


class ClubTestsAPI(ApiTestCasesMixin, APITestCase):
    fixtures = ['contest/fixtures/clubs.json']

    def test_getting_info(self):
        response = self.client.get(reverse('api:club-list'))
        self.assertEqual(
            response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )

        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('api:club-list'))
        self.assertEqual(len(response.data['results']), 2)


class SchoolTestsAPI(ApiTestCasesMixin, APITestCase):
    fixtures = ['schools.json']

    def test_getting_info(self):
        response = self.client.get(reverse('api:school-list'))
        self.assertEqual(
            response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )

        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('api:school-list'))
        self.assertEqual(len(response.data['results']), 2)


class UserTestsAPI(ApiTestCasesMixin, APITestCase):
    fixtures = [
        'contest/fixtures/clubs.json',
        'contest/fixtures/users.json'
    ]

    def test_getting_info(self):
        response = self.client.get(reverse('api:rushuser-list'))
        self.assertEqual(
            response.data['detail'],
            'Nie podano danych uwierzytelniających.'
        )

        self.admin = RushUser.objects.create_superuser(
            username='admin', email='test@bb.cc', password='password'
        )
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('api:rushuser-list'))
        self.assertEqual(len(response.data['results']), 3)

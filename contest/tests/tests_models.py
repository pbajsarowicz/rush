# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from contest.models import (
    RushUser,
    Organizer,
    Contest,
    Club,
    Contestant,
)


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
        self.assertFalse(user_test.is_staff)
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


class ContestTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.contest = Contest.objects.create(
            organizer=Organizer(id=1), date=self.now, place='Szkoła',
            age_min=11, age_max=16, deadline=self.now
        )

    def test_contest_methods(self):
        self.assertEqual(
            self.contest.__unicode__(),
            'Szkoła {}'.format(datetime.strftime(self.now, '%d.%m.%Y %X'))
        )


class OrganizerTestCase(TestCase):
    def setUp(self):
        club = Club.objects.create(name='adam', code=12345)
        self.organizer = Organizer.objects.create(
            name='Adam', club=club
        )

    def test_organizer_methods(self):
        self.assertEqual(self.organizer.__unicode__(), 'Adam')


class ContestantTestCase(TestCase):
    def setUp(self):
        self.contestant = Contestant.objects.create(
            moderator=RushUser(id=1), first_name='Adam', last_name='Kowalski',
            gender='M', age=15, school='Szkoła', styles_distances='10m żabka',
            contest=Contest(id=1)
        )

    def test_contestant_methods(self):
        self.assertEqual(self.contestant.__unicode__(), 'Adam Kowalski')


class ClubTestCase(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Klub', code=15545)

    def test_club_methods(self):
        self.assertEqual(self.club.__unicode__(), 'Klub')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone

from contest.models import (
    Club,
    Contact,
    Contest,
    Contestant,
    RushUser,
    School,
    ContestantScore,
    Style,
    Distance,
    ContestStyleDistances
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
        self.assertFalse(user_test.has_perm('contest.add_contest'))
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
    fixtures = ['clubs.json']

    def setUp(self):
        self.now = timezone.now()
        self.contest = Contest.objects.create(
            date=self.now, place='Szkoła', lowest_year=2005, highest_year=2000,
            deadline=self.now
        )

    def test_contest_methods(self):
        expected_name = '{} - {}'.format(
            'Szkoła', self.now.strftime('%d-%m-%Y')
        )
        self.assertEqual(self.contest.__unicode__(), expected_name)

        self.contest.name = 'Wodnik'
        self.contest.save()

        self.assertEqual(self.contest.__unicode__(), 'Wodnik')


class ContestantTestCase(TestCase):
    fixtures = ['contests.json', 'clubs.json', 'users.json']

    def setUp(self):
        self.contestant = Contestant.objects.create(
            moderator=RushUser.objects.first(), first_name='Adam',
            last_name='Kowalski', gender='M', year_of_birth=2001, school='S',
            contest=Contest.objects.first()
        )

    def test_contestant_methods(self):
        self.assertEqual(self.contestant.__unicode__(), 'Adam Kowalski')


class ClubTestCase(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Klub', code=15545)

    def test_club_methods(self):
        self.assertEqual(self.club.__unicode__(), 'Klub')


class SchoolTestCase(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Szkola')

    def test_club_methods(self):
        self.assertEqual(self.school.__unicode__(), 'Szkola')


class ContactTestCase(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            email='email@wp.pl', website='www.example.com',
            phone_number='123456789'
        )

    def test_club_methods(self):
        self.assertEqual(
            self.contact.__unicode__(),
            'email@wp.pl www.example.com 123456789'
        )


class UnitModelsMixinTestCase(TestCase):
    fixtures = [
        'contest/fixtures/contests.json',
        'contest/fixtures/users.json',
        'contest/fixtures/clubs.json',
        'contest/fixtures/schools.json',
    ]

    def test_unit_name_select(self):
        contest = Contest.objects.first()
        self.assertEqual(
            contest.unit_name_select,
            '<select id="id_unit" name="unit"><option value="2_school" >'
            '[Szko\u0142a] Klub wodnika</option><br><option value="1_school" '
            'selected>[Szko\u0142a] ZSP1 w Pile</option><option value="2_club"'
            ' >[Klub] Klub wodnika</option><br><option value="1_club" >[Klub] '
            'ZSP1 w Pile</option></select>'
        )


class ContestantScoreTestCase(TestCase):
    fixtures = [
        'contestants.json', 'styles.json', 'contests.json',
        'distances.json', 'users.json'
    ]

    def setUp(self):
        self.score = ContestantScore.objects.create(
            contestant=Contestant.objects.first(), style=Style.objects.first(),
            distance=Distance.objects.first(), time_result=655111
        )

    def test_score_display(self):
        self.assertEqual(
            self.score.__unicode__(), 'Adam Kowalski: Dowolny 25m - 10:55.11s'
        )


class ContestStyleDistancesTestCase(TestCase):
    fixtures = ['styles.json', 'distances.json']

    def setUp(self):
        self.style = ContestStyleDistances.objects.create(
            style=Style.objects.first()
        )
        self.style.distances.set(Distance.objects.all()[:3])

    def test_style_display(self):
        self.assertEqual(
            self.style.__unicode__(),
            'Dowolny: [<Distance: 25m>, <Distance: 50m>, <Distance: 100m>]'
        )

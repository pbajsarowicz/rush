# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from contest.models import (
    Club,
    Contact,
    Contest,
    contest_directory_path,
    Contestant,
    ContestFiles,
    RushUser,
    School,
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
        self.user.notifications = True
        self.user.set_password('Password')
        self.user.save()

    def test_user(self):
        """
        Checking status and informations for user.
        """
        user_test = RushUser.objects.get(email='test@xyz.pl')
        user_test.cancel_notifications()
        self.assertEqual(user_test.get_full_name(), 'Name Last Name')
        self.assertEqual(user_test.get_short_name(), 'Last Name')
        self.assertFalse(user_test.has_perm('contest.add_contest'))
        self.assertTrue(user_test.has_module_perms(None))
        self.assertEqual(user_test.notifications, False)
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
    fixtures = ['clubs.json', 'users.json']

    def setUp(self):
        self.now = timezone.now()
        self.contest = Contest.objects.create(
            name='Zawody', date=self.now, place='Szkoła', lowest_year=2005,
            highest_year=2000, deadline=self.now
        )

    def test_contest_methods(self):
        expected_name = 'Zawody - Szkoła - {}'.format(
            self.now.strftime('%d-%m-%Y')
        )
        self.assertEqual(self.contest.__unicode__(), expected_name)

        expected_name = 'Wodnik - Szkoła - {}'.format(
            self.now.strftime('%d-%m-%Y')
        )
        self.contest.name = 'Wodnik'
        self.contest.save()

        self.assertEqual(self.contest.__unicode__(), expected_name)

    def test_contest_directory_path(self):
        filename = 'abcde' * 60
        self.contest.name = 'ab' * 26
        self.contest.save()

        contest_file = ContestFiles.objects.create(
            contest=self.contest,
            uploaded_by=RushUser.objects.last(),
            contest_file=SimpleUploadedFile('test_file.pdf', str(filename))
        )

        result = contest_directory_path(contest_file, filename)

        self.assertEqual(
            result, 'contest/{}/{}/{}'.format(
                'ab' * 25,
                contest_file.date_uploaded.strftime('%Y/%m/%d'),
                'abcde' * 51
            )
        )


class ContestantTestCase(TestCase):
    fixtures = ['contests.json', 'clubs.json', 'users.json']

    def setUp(self):
        self.contestant = Contestant.objects.create(
            moderator=RushUser.objects.first(), first_name='Adam',
            last_name='Kowalski', gender='M', year_of_birth=2001, school='S',
            styles=['D25', 'G50'], contest=Contest.objects.first()
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
            '>[Szko\u0142a] ZSP1 w Pile</option><option value="2_club" >'
            '[Klub] Klub wodnika</option><br><option value="1_club" >[Klub] '
            'ZSP1 w Pile</option></select>'

        )

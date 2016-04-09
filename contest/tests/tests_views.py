# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import make_aware
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from contest.forms import (
    ContestantForm,
    LoginForm,
    RegistrationForm,
    SettingPasswordForm,
)
from contest.models import (
    Contestant,
    RushUser,
    Contest,
    Organizer,
    Club,
)
from contest.views import SetPasswordView


class HomeViewTests(TestCase):
    def setUp(self):
        self.contest = Contest.objects.create(
            organizer=Organizer(id=1), date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', age_min=11, age_max=16, description='Opis',
            deadline=make_aware(datetime(2048, 11, 20))
        )
        self.contest_done = Contest.objects.create(
            organizer=Organizer(id=2), date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', age_min=11, age_max=16, description='Opis',
            deadline=make_aware(datetime(2008, 11, 20))
        )
        self.user = RushUser.objects.create_superuser(
            email='xyz@xyz.pl', username='login', password='Password'
        )
        self.client.login(username='login', password='Password')
        self.response = self.client.get(reverse('contest:home'))

    def test_context(self):
        self.assertEqual(len(self.response.context['completed']), 1)
        self.assertEqual(len(self.response.context['upcoming']), 1)
        self.assertTrue(
            isinstance(self.response.context['completed'][0], Contest)
        )


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = RushUser.objects.create_user(
            email='xyz@xyz.pl', first_name='Name', last_name='LastName',
            organization_name='School', organization_address='Address',
            username='username'
        )
        self.user.is_active = True
        self.user.set_password('Password')
        self.user.save()

    def test_authenticate(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.
        """
        self.assertEqual(
            authenticate(username='username', password='Password'),
            self.user
        )
        self.assertIsNone(
            authenticate(username='username', password='random_pass')
        )
        self.assertIsNone(
            authenticate(username='example@example.pl', password='qwerty')
        )
        self.assertIsNone(authenticate(username='', password=''))

    def test_login_view(self):
        """
        Checking if form is valid for correct data and invalid for
        wrong data or inactive user
        """
        response = self.client.get(reverse('contest:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], LoginForm)
        )
        self.assertEqual(list(LoginForm.base_fields), ['username', 'password'])

        form_data = {'username': 'username', 'password': 'wrong_password'}
        response = self.client.post(reverse('contest:login'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['__all__'],
            [
                'Wprowadź poprawny login oraz hasło. '
                'Uwaga: wielkość liter ma znaczenie.'
            ]
        )

        form_data = {'username': 'username', 'password': 'Password'}
        response = self.client.post(reverse('contest:login'), data=form_data)
        self.assertEqual(response.status_code, 302)


class PasswordSettingTests(TestCase):
    def setUp(self):
        self.user_1 = RushUser(
            email='ddd@ddd.pl', first_name='Łukasz', last_name='Ślązak',
            is_active=True
        )
        self.user_1.set_password('password123')
        self.user_1.save()

        self.user_2 = RushUser.objects.create(
            email='kkk@kkk.pl', first_name='Ewa', last_name='Olczak',
            username='username_taken'
        )
        self.user_2.is_active = True
        self.user_2.set_password('Password_already_set')
        self.user_2.save()
        self.user1_uid = urlsafe_base64_encode(force_bytes(self.user_1.pk))
        self.user1_token = default_token_generator.make_token(self.user_1)

    def test_correct_url(self):
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], SettingPasswordForm)
        )

        wrong_token = default_token_generator.make_token(self.user_2)
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': wrong_token}
            )
        )
        self.assertEqual(response.status_code, 302)

        wrong_uid = urlsafe_base64_encode(force_bytes(self.user_2.pk))
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': wrong_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SetPasswordView._get_user('00'))

        self.client.login(
            username='username_taken', password='Password_already_set'
        )
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            )
        )
        self.assertFalse(isinstance(response.context['user'], RushUser))

    def test_setting_password(self):
        form_data = {
            'new_password1': 'pass1234', 'new_password2': 'sad_panda',
            'username': 'username_taken'
        }
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'username': ['Podana nazwa użytkownika jest już zajęta.'],
                'new_password2': ['Hasła nie są identyczne.']
            }
        )

        form_data = {
            'new_password1': 'pass1234', 'new_password2': 'pass1234',
            'username': 'username123'
        }
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Hasło ustawione, można się zalogować.'
        )


class AccountsViewTestCase(TestCase):
    def setUp(self):
        user = RushUser(
            email='auth@user.pl', first_name='auth', last_name='auth',
            is_active=True, username='auth'
        )
        user.set_password('password123')
        user.save()

        self.client.login(username='auth', password='password123')

    def test_get(self):
        inactive_user = RushUser.objects.create(
            email='inactive_user@user.pl', first_name='Test',
            last_name='Anonymous', is_active=False, username='inactive_user'
        )

        response = self.client.get(reverse('contest:accounts'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0], inactive_user)

    def test_post(self):
        user = RushUser(
            email='test@user.pl', first_name='Test', last_name='Anonymous',
            is_active=False
        )
        user.set_password('password123')
        user.save()

        response = self.client.post(
            reverse('contest:accounts', kwargs={'user_id': user.id})
        )

        user = RushUser.objects.get(pk=user.id)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(user.is_active)

        response = self.client.post(
            reverse('contest:accounts', kwargs={'user_id': 0})
        )
        self.assertEqual(response.status_code, 500)

    def test_delete(self):
        user = RushUser(
            email='test@user.pl', first_name='Test', last_name='Anonymous',
            is_active=False
        )
        user.set_password('password123')
        user.save()

        response = self.client.delete(
            reverse('contest:accounts', kwargs={'user_id': user.id})
        )
        self.assertFalse(RushUser.objects.filter(pk=user.id).exists())
        self.assertEqual(response.status_code, 204)

        response = self.client.delete(
            reverse('contest:accounts', kwargs={'user_id': user.id})
        )
        self.assertEqual(response.status_code, 500)


class RegisterViewTests(TestCase):
    def test_register_view(self):
        response = self.client.get(reverse('contest:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], RegistrationForm)
        )
        response = self.client.post(reverse('contest:register'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'first_name': ['To pole jest wymagane.'],
                'last_name': ['To pole jest wymagane.'],
                'organization_address': ['To pole jest wymagane.'],
                'email': ['To pole jest wymagane.']
            }
        )

        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'abc@tmp.com', 'first_name': 'Imie',
                'last_name': 'Nazwisko', 'organization_name': 'School',
                'organization_address': 'Address', 'club_code': 12345,
            }
        )
        self.assertEqual(response.context['email'], settings.SUPPORT_EMAIL)


class ContestantAddViewTestCase(TestCase):
    def setUp(self):
        self.user = RushUser(
            email='test@cos.pl', username='test_test',
            password='P@ssw0rd', is_active=True
        )
        self.user.set_password('P@ssw0rd')
        self.user.save()

        self.client.login(username='test_test', password='P@ssw0rd')

        self.form_data = {
            'csrfmiddlewaretoken': 'A33GMETyB7NE1CknWDg2jVuS1Jsm5A9y',
            'form-0-age': '11',
            'form-0-first_name': 'Jan',
            'form-0-gender': 'M',
            'form-0-last_name': 'Kowalski',
            'form-0-school': 'Test',
            'form-0-styles_distances': '1000m',
            'form-1-age': '16',
            'form-1-first_name': 'Anna',
            'form-1-gender': 'F',
            'form-1-last_name': 'Nowak',
            'form-1-school': 'Test',
            'form-1-styles_distances': '500m',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-MIN_NUM_FORMS': '0',
            'form-TOTAL_FORMS': '2'
        }

        self.contest = Contest.objects.create(
            organizer=Organizer(id=1), date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', age_min=11, age_max=16, description='Opis',
            deadline=make_aware(datetime(2048, 11, 20))
        )
        self.contest_done = Contest.objects.create(
            organizer=Organizer(id=2), date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', age_min=11, age_max=16, description='Opis',
            deadline=make_aware(datetime(2008, 11, 20))
        )
        self.contest_deadline = Contest.objects.create(
            organizer=Organizer(id=3), date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', age_min=11, age_max=16, description='Opis',
            deadline=make_aware(datetime(2008, 11, 20))
        )

    def test_get(self):
        response = self.client.get(
            reverse('contest:contestant-add', kwargs={'contest_id': 1}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(
            response.context['formset'].forms[0], ContestantForm
        )

        response = self.client.get(
            reverse('contest:contestant-add', kwargs={'contest_id': 865}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Takie zawody nie istnieją.'
        )

        response = self.client.get(
            reverse('contest:contestant-add', kwargs={'contest_id': 2}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Zawody się już skończyły.'
        )

        response = self.client.get(
            reverse('contest:contestant-add', kwargs={'contest_id': 3}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Czas na dodawanie zawodników już minął.'
        )

    def test_post_with_success(self):
        response = self.client.post(
            reverse('contest:contestant-add', kwargs={'contest_id': 1}),
            data=self.form_data
        )

        self.assertEqual(response.status_code, 200)
        contestants = Contestant.objects.filter(moderator=self.user)

        self.assertEquals(len(contestants), 2)

        self.assertEqual(contestants[0].first_name, 'Jan')
        self.assertEqual(contestants[1].first_name, 'Anna')

    def test_post_with_validation_error(self):
        response = self.client.post(
            reverse('contest:contestant-add', kwargs={'contest_id': 865}),
            data=self.form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Takie zawody nie istnieją.'
        )

        self.form_data['form-0-age'] = 99
        response = self.client.post(
            reverse('contest:contestant-add', kwargs={'contest_id': 1}),
            data=self.form_data
        )

        expected_error = {
            'age': ['Zawodnik nie mieści się w wymaganym przedziale wiekowym.']
        }
        self.assertEqual(
            response.context['formset'].errors, [expected_error, {}]
        )

        self.form_data['form-0-age'] = 15
        self.form_data['form-0-gender'] = 'WRONG'
        response = self.client.post(
            reverse('contest:contestant-add', kwargs={'contest_id': 1}),
            data=self.form_data
        )
        expected_error = {
            'gender': [(
                'Wybierz poprawną wartość. WRONG nie jest jednym z '
                'dostępnych wyborów.'
            )]
        }

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context['formset'].is_valid())
        self.assertEqual(
            response.context['formset'].errors, [expected_error, {}]
        )
        self.assertFalse(
            Contestant.objects.filter(moderator=self.user).exists()
        )


class ContestantListViewTestCase(TestCase):

    def setUp(self):
        self.user = RushUser(
            email='test@cos.pl', username='test_test',
            password='P@ssw0rd', is_active=True
        )
        self.user.set_password('P@ssw0rd')
        self.user.save()

        self.client.login(username='test_test', password='P@ssw0rd')

        club = Club.objects.create(name='adam', code=12345)
        organizer = Organizer.objects.create(
            name='Adam', club=club
        )

        contest = Contest.objects.create(
            organizer=organizer,
            date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', age_min=11, age_max=16, description='Opis',
            deadline=make_aware(datetime(2048, 11, 20))
        )
        self.contestant = Contestant.objects.create(
            moderator=self.user, first_name='Adam', last_name='Nowak',
            gender='M', age=14, school='Szkoła', styles_distances='100m motyl',
            contest=contest
        )

    def test_get(self):
        response = self.client.get(
            reverse('contest:contestant-list', kwargs={'contest_id': 1}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['contestants']), 1)


class EditContestantViewTestCase(TestCase):
    fixtures = [
        'organizers.json', 'contests.json', 'clubs.json', 'users.json',
    ]

    def setUp(self):
        self.user = RushUser(
            email='root@root.pl', username='root',
            password='R@ootroot', is_active=True
        )
        self.user.set_password('R@ootroot')
        self.user.save()
        self.contestant = Contestant.objects.create(
            first_name='Adam',
            last_name='Nowak',
            gender='M',
            age=14,
            school='Szkoła',
            styles_distances='100m motyl',
            contest=Contest.objects.first(),
            moderator=self.user
        )

        self.client.login(username='root', password='R@ootroot')

    def test_get(self):
        response = self.client.get(
            reverse(
                'contest:contestant-edit',
                kwargs={'contestant_id': self.contestant.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].initial['first_name'], 'Adam'
        )
        self.assertEqual(
            response.context['form'].initial['last_name'], 'Nowak'
        )
        self.assertEqual(response.context['form'].initial['gender'], 'M')
        self.assertEqual(response.context['form'].initial['school'], 'Szkoła')
        self.assertEqual(
            response.context['form'].initial['styles_distances'], '100m motyl'
        )
        self.assertEqual(response.context['form'].initial['age'], 14)

    def test_post(self):
        response = self.client.post(
            reverse(
                'contest:contestant-edit',
                kwargs={'contestant_id': self.contestant.id}
            ),
            data={
                'first_name': 'Karol', 'last_name': 'Kowalski',
                'school': 'School', 'gender': 'F', 'age': 11,
            }
        )
        self.assertEqual(response.context['first_name'], 'Karol')
        self.assertEqual(response.context['last_name'], 'Kowalski')
        self.assertEqual(response.context['school'], 'School')
        self.assertEqual(response.context['gender'], 'F')
        self.assertEqual(response.context['age'], 11)

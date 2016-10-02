# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import (
    date,
    datetime,
)

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import (
    Group,
    Permission,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.timezone import make_aware
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from mock import patch

from contest.forms import (
    ContestantForm,
    ContestForm,
    INDIVIDUAL_CONTESTANTS_GROUP,
    LoginForm,
    RegistrationForm,
    RushResetPasswordEmailForm,
    RushResetPasswordForm,
    RushSetPasswordForm,
)
from contest.models import (
    Club,
    Contest,
    Contestant,
    RushUser,
)
from contest.views import (
    RegisterView,
    SetResetPasswordView,
    server_error,
    bad_request,
    permission_denied
)
from rush import urls


class HomeViewTests(TestCase):
    fixtures = [
        'clubs.json',
    ]

    def setUp(self):
        self.contest = Contest.objects.create(
            date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', lowest_year=2000, highest_year=2005,
            description='Opis',
            deadline=make_aware(datetime(2048, 11, 20))
        )
        self.contest_done = Contest.objects.create(
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=2000, highest_year=2005,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20))
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
        response = self.client.get(
            reverse('contest:login'), {'next': '/redirect/page/'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], LoginForm)
        )
        self.assertEqual(response.context['next'], '/redirect/page/')

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

        data = {
            'username': 'username',
            'password': 'Password',
            'next': '/redirect/page/',
        }
        response = self.client.post(reverse('contest:login'), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/redirect/page/')
        self.client.logout()

        data = {
            'username': 'xyz@xyz.pl',
            'password': 'Password',
            'next': '/redirect/page/',
        }
        response = self.client.post(reverse('contest:login'), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/redirect/page/')


class SetResetPasswordViewTestCase(TestCase):

    def setUp(self):
        self.user_1 = RushUser(
            email='ddd@ddd.pl', first_name='Łukasz', last_name='Ślązak',
            is_active=True
        )
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

    def test_set_password_individual_user(self):
        individual_user = RushUser(
            email='individual_user@yolo.pl', first_name='A', last_name='B',
            username='temp_username'
        )
        individual_user.save()
        individual_user.groups.add(INDIVIDUAL_CONTESTANTS_GROUP)

        individual_user_uid = urlsafe_base64_encode(
            force_bytes(individual_user.pk)
        )
        individual_user_token = default_token_generator.make_token(
            individual_user
        )
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={
                    'uidb64': individual_user_uid,
                    'token': individual_user_token,
                }
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], RushSetPasswordForm)
        )

        form_data = {
            'new_password1': 'pass1234', 'new_password2': 'pass1234',
            'username': 'individual_user'
        }
        response = self.client.post(
            reverse(
                'contest:set-password',
                kwargs={
                    'uidb64': individual_user_uid,
                    'token': individual_user_token,
                }
            ),
            data=form_data,
        )
        individual_user = RushUser.objects.get(username='individual_user')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(individual_user.is_active)

    def test_correct_url(self):
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            isinstance(response.context['form'], RushSetPasswordForm)
        )

    def test_resend_on_wrong_token(self):
        wrong_token = default_token_generator.make_token(self.user_2)
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': self.user1_uid, 'token': wrong_token}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_resend_on_wrong_uid(self):
        wrong_uid = urlsafe_base64_encode(force_bytes(self.user_2.pk))
        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': wrong_uid, 'token': self.user1_token}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SetResetPasswordView._get_user('00'))

        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': 'XX', 'token': self.user1_token}
            )
        )
        self.assertEqual(
            response.context['message'], 'Użytkownik nie istnieje.'
        )

        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': 'XX', 'token': self.user1_token}
            )
        )
        self.assertEqual(
            response.context['message'], 'Użytkownik nie istnieje.'
        )

        response = self.client.get(
            reverse(
                'contest:set-password',
                kwargs={'uidb64': 'XX', 'token': self.user1_token}
            )
        )
        self.assertEqual(
            response.context['message'], 'Użytkownik nie istnieje.'
        )

    def test_password_already_set(self):
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

    def test_sending_mail(self):
        RegisterView.send_email_with_new_user(
            'Janek', 'Kowalski', ['admin@admin.pl'], 'www.rush.pl'
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['admin@admin.pl'])

    def test_reset_password_successful_get(self):
        user_2_uid = urlsafe_base64_encode(force_bytes(self.user_2.pk))
        user_2_token = default_token_generator.make_token(self.user_2)

        response = self.client.get(
            reverse(
                'contest:reset-password',
                kwargs={'uidb64': user_2_uid, 'token': user_2_token}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], RushResetPasswordForm)

    def test_reset_password_expired_token_get(self):
        user_2_uid = urlsafe_base64_encode(force_bytes(self.user_2.pk))

        with patch('django.contrib.auth.tokens.date') as mock_date:
            mock_date.today.return_value = date(2010, 1, 1)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            user_2_token = default_token_generator.make_token(self.user_2)

        response = self.client.get(
            reverse(
                'contest:reset-password',
                kwargs={'uidb64': user_2_uid, 'token': user_2_token}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Link nie jest już aktywny. Jeśli masz problemy z zalogowaniem, '
            'skorzystaj z formularza resetowania hasła.'
        )

    def test_reset_password_post(self):
        user_2_uid = urlsafe_base64_encode(force_bytes(self.user_2.pk))
        user_2_token = default_token_generator.make_token(self.user_2)
        form_data = {
            'new_password1': 'pass1234', 'new_password2': 'pass1234'
        }

        response = self.client.post(
            reverse(
                'contest:reset-password',
                kwargs={'uidb64': user_2_uid, 'token': user_2_token}
            ),
            data=form_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Hasło ustawione, można się zalogować.'
        )


class ResetPasswordEmailViewTestCase(TestCase):

    def setUp(self):
        self.user = RushUser.objects.create(
            email='bruce@lee.com', first_name='Bruce', last_name='Lee',
            username='brucelee'
        )
        self.user.is_active = True
        self.user.set_password('Password_already_set')
        self.user.save()

    def test_get(self):
        response = self.client.get(reverse('contest:reset-email'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(
            response.context['form'], RushResetPasswordEmailForm
        )

    def test_post_successful(self):
        form_data = {'email': 'bruce@lee.com'}

        response = self.client.post(
            reverse('contest:reset-email'), data=form_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            (
                'Link do zresetowania hasła został wysłany. Sprawdź skrzynkę '
                'e-mailową.'
            )
        )

    def test_post_validation_error(self):
        form_data = {'email': 'fake@mail.com'}

        response = self.client.post(
            reverse('contest:reset-email'), data=form_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors,
            {
                'email': [(
                    'Konto dla podanego adresu nie istnieje lub nie zostało '
                    'jeszcze aktywowane. Sprawdź poprawność podanego adresu. '
                    'W razie problemów skontaktuj się z nami Sample@email.com'
                )]
            }
        )


class AccountsViewTestCase(TestCase):
    def setUp(self):
        user = RushUser(
            email='auth@user.pl', first_name='auth', last_name='auth',
            is_active=True, username='auth', is_admin=True
        )
        user.set_password('password123')
        user.save()

        normal_user = RushUser.objects.create(
            email='cc@aa.bbb', first_name='Adam', last_name='NieAdmin',
            is_active=True, username='normal_user', is_admin=False
        )
        normal_user.set_password('password123')
        normal_user.save()

        self.client.login(username='auth', password='password123')

    def test_get(self):
        self.client.login(username='normal_user', password='password123')
        response = self.client.get(reverse('contest:accounts'))
        self.assertRedirects(response, '/zaloguj/?next=/administrator/konta/')

        inactive_user = RushUser.objects.create(
            email='inactive_user@user.pl', first_name='Test',
            last_name='Anonymous', is_active=False, username='inactive_user'
        )
        self.client.login(username='auth', password='password123')
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

    def test_delete_and_rejection_email(self):
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
        self.assertEqual(mail.outbox[0].to, [user.email])

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
                'email': ['To pole jest wymagane.'],
                'representative': ['To pole jest wymagane.']
            }
        )

    def test_register_club_user(self):
        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'abc@tmp.com', 'first_name': 'Imie',
                'last_name': 'Nazwisko', 'organization_name': '',
                'organization_address': '', 'club_code': '',
                'representative': RegistrationForm.CLUB
            }
        )
        self.assertEqual(
            response.context['form'].errors,
            {
                'organization_name': ['To pole jest wymagane.'],
                'organization_address': ['To pole jest wymagane.'],
                'club_code': ['To pole jest wymagane.'],
            }
        )

        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'abc@tmp.com', 'first_name': 'Imie',
                'last_name': 'Nazwisko', 'organization_name': 'Club',
                'organization_address': 'Address', 'club_code': 12345,
                'representative': RegistrationForm.CLUB
            }
        )
        self.assertEqual(response.context['email'], settings.SUPPORT_EMAIL)
        self.assertEqual(
            RushUser.objects.get(email='abc@tmp.com').unit_name, 'Club'
        )

    def test_register_school_user(self):
        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'abc@tmp.com', 'first_name': 'Imie',
                'last_name': 'Nazwisko', 'organization_name': '',
                'organization_address': '',
                'representative': RegistrationForm.SCHOOL
            }
        )
        self.assertEqual(
            response.context['form'].errors,
            {
                'organization_name': ['To pole jest wymagane.'],
                'organization_address': ['To pole jest wymagane.'],
            }
        )

        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'abc2@tmp.com', 'first_name': 'Imie2',
                'last_name': 'Nazwisko2', 'organization_name': 'School',
                'organization_address': 'Address',
                'representative': RegistrationForm.SCHOOL
            }
        )
        self.assertEqual(response.context['email'], settings.SUPPORT_EMAIL)
        self.assertEqual(
            RushUser.objects.get(email='abc2@tmp.com').unit_name, 'School'
        )

    def test_register_individual_user(self):
        response = self.client.post(
            reverse('contest:register'),
            data={
                'email': 'individual@user.com', 'first_name': 'Imie2',
                'last_name': 'Nazwisko2',
                'representative': RegistrationForm.INDIVIDUAL
            }
        )
        rush_user = RushUser.objects.get(email='individual@user.com')

        self.assertEqual(response.context['email'], settings.SUPPORT_EMAIL)
        self.assertEqual(rush_user.unit_name, None)
        self.assertTrue(
            rush_user.groups.filter(name='Individual contestants').exists()
        )


class ContestantAddViewTestCase(TestCase):
    fixtures = ['clubs.json']

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
            'form-0-year_of_birth': '2005',
            'form-0-first_name': 'Jan',
            'form-0-gender': 'M',
            'form-0-last_name': 'Kowalski',
            'form-0-school': 'P',
            'form-0-styles': ',D25,G25',
            'form-0-organization': self.user.unit,
            'form-1-year_of_birth': '2000',
            'form-1-first_name': 'Anna',
            'form-1-gender': 'F',
            'form-1-last_name': 'Nowak',
            'form-1-school': 'P',
            'form-1-styles': ',K50,Z200',
            'form-1-organization': self.user.unit,
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-MIN_NUM_FORMS': '0',
            'form-TOTAL_FORMS': '2'
        }

        styles = ['D25', 'D50', 'G25', 'K50', 'K200', 'Z200']

        self.contest = Contest.objects.create(
            date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', lowest_year=2000, highest_year=2005,
            description='Opis', deadline=make_aware(datetime(2048, 11, 20)),
            styles=styles
        )
        self.contest_done = Contest.objects.create(
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=2000, highest_year=2005,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20)),
            styles=styles
        )
        self.contest_deadline = Contest.objects.create(
            date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', lowest_year=2000, highest_year=2005,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20)),
            styles=styles
        )

    def test_get(self):
        response = self.client.get(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            )
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
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest_done.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Zawody się już skończyły.'
        )

        response = self.client.get(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest_deadline.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Czas na dodawanie zawodników już minął.'
        )

    def test_post_with_success(self):
        response = self.client.post(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            ),
            data=self.form_data
        )

        self.assertEqual(response.status_code, 200)
        contestants = Contestant.objects.filter(moderator=self.user)
        self.assertEquals(len(contestants), 2)

        self.assertEqual(contestants[0].first_name, 'Jan')
        self.assertEqual(contestants[1].first_name, 'Anna')

    def test_post_already_signed_in(self):
        individual_user = RushUser(
            email='individual_user@yolo.pl', first_name='Aaa', last_name='Bbb',
            username='individual_user', is_active=True
        )
        individual_user.set_password('P@ssw0rd')
        individual_user.save()
        individual_user.groups.add(INDIVIDUAL_CONTESTANTS_GROUP)

        self.form_data = {
            'csrfmiddlewaretoken': 'A33GMETyB7NE1CknWDg2jVuS1Jsm5A9y',
            'form-0-year_of_birth': '2005',
            'form-0-first_name': individual_user.first_name,
            'form-0-gender': 'M',
            'form-0-last_name': individual_user.last_name,
            'form-0-styles': ',D25,G25',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-MIN_NUM_FORMS': '0',
            'form-TOTAL_FORMS': '1'
        }

        self.client.login(username='individual_user', password='P@ssw0rd')

        response = self.client.post(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            ),
            data=self.form_data
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'], 'Jesteś już zapisany na ten konkurs'
        )

    def test_get_required_fields_individual(self):
        user = RushUser(
            email='individual_user@email.pl', username='individual_user',
            password='P@ssw0rd', is_active=True
        )
        user.set_password('P@ssw0rd')
        user.save()
        user.groups.add(INDIVIDUAL_CONTESTANTS_GROUP)

        self.client.login(username='individual_user', password='P@ssw0rd')

        response = self.client.get(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            )
        )
        form = response.context['formset'].forms[0]

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(form, ContestantForm)
        self.assertTrue(form.fields['first_name'].widget.attrs['readonly'])
        self.assertTrue(form.fields['last_name'].widget.attrs['readonly'])

    def test_get_required_fields_non_individual(self):
        user = RushUser(
            email='nonindividual_user@email.pl', username='nonindividual_user',
            password='P@ssw0rd', is_active=True
        )
        user.set_password('P@ssw0rd')
        club = Club.objects.last()
        user.object_id = club.pk
        user.content_type = ContentType.objects.get_for_model(Club)

        user.save()
        user.groups.add(INDIVIDUAL_CONTESTANTS_GROUP)

        self.client.login(username='nonindividual_user', password='P@ssw0rd')
        response = self.client.get(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            )
        )

        form = response.context['formset'].forms[0]

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(form, ContestantForm)
        self.assertEqual(form.fields['organization'].initial, club)

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

        self.form_data['form-0-year_of_birth'] = 1978
        response = self.client.post(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            ),
            data=self.form_data
        )

        expected_error = {
            'year_of_birth': [
                'Zawodnik nie mieści się w wymaganym przedziale wiekowym.'
            ]
        }
        self.assertEqual(
            response.context['formset'].errors, [expected_error, {}]
        )

        self.form_data['form-0-year_of_birth'] = 2001
        self.form_data['form-0-gender'] = 'WRONG'
        response = self.client.post(
            reverse(
                'contest:contestant-add',
                kwargs={'contest_id': self.contest.id}
            ),
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

        self.contest = Contest.objects.create(
            date=make_aware(datetime(2050, 12, 31)),
            place='Szkoła', lowest_year=2000, highest_year=2005,
            description='Opis', deadline=make_aware(datetime(2048, 11, 20)),
            content_type=ContentType.objects.get_for_model(club),
            object_id=club.pk
        )
        self.contestant = Contestant.objects.create(
            moderator=self.user, first_name='Adam', last_name='Nowak',
            gender='M', year_of_birth=2002, school='S', styles=['M50', 'Z100'],
            contest=self.contest
        )

    def test_get(self):
        response = self.client.get(
            reverse(
                'contest:contestant-list',
                kwargs={'contest_id': self.contest.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['contestants']), 1)


class EditContestantViewTestCase(TestCase):
    fixtures = [
        'contests.json', 'clubs.json', 'users.json',
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
            year_of_birth=2002,
            school='P',
            styles=',K200,D25',
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
        self.assertEqual(response.context['form'].initial['school'], 'P')
        self.assertEqual(
            response.context['form'].initial['year_of_birth'], 2002
        )
        self.assertEqual(
            response.context['form'].initial['year_of_birth'], 2002
        )

    def test_post(self):
        response = self.client.post(
            reverse(
                'contest:contestant-edit',
                kwargs={'contestant_id': self.contestant.id}
            ),
            data={
                'first_name': 'Karol', 'last_name': 'Kowalski',
                'school': 'P', 'gender': 'F', 'year_of_birth': 2005,
            }
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context['form'].cleaned_data['first_name'], 'Karol'
        )
        self.assertEqual(
            response.context['form'].cleaned_data['last_name'], 'Kowalski')
        self.assertEqual(
            response.context['form'].cleaned_data['school'], 'P'
        )
        self.assertEqual(response.context['form'].cleaned_data['gender'], 'F')
        self.assertEqual(
            response.context['form'].cleaned_data['year_of_birth'], 2005
        )


class ContestResultsViewTestCase(TestCase):
    def setUp(self):
        self.contest = Contest.objects.create(
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=11, highest_year=16,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20)),
            results='yolo'
        )
        self.contest2 = Contest.objects.create(
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=11, highest_year=16,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20))
        )

        self.user = RushUser.objects.create_superuser(
            email='xyz@xyz.pl', username='login', password='Password'
        )
        self.client.login(username='login', password='Password')

    def test_get_msg_with_results(self):
        response = self.client.get(
            reverse(
                'contest:contest-results',
                kwargs={'contest_id': self.contest.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['msg'],
            ''
        )

    def test_get_msg_without_results(self):
        response = self.client.get(
            reverse(
                'contest:contest-results',
                kwargs={'contest_id': self.contest2.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['msg'],
            'Nie dodano jeszcze wyników.'
        )

    def test_get_results(self):
        response = self.client.get(
            reverse(
                'contest:contest-results',
                kwargs={'contest_id': self.contest.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['results'],
            self.contest.results
        )


class AddContestResultsViewTest(TestCase):
    def setUp(self):
        self.admin = RushUser.objects.create_superuser(
            email='xyz@xyz.pl', username='admin', password='Password'
        )
        self.contest = Contest.objects.create(
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=11, highest_year=16,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20)),
            created_by=self.admin
        )

        self.user = RushUser(
            email='root@root.pl', username='user',
            password='useruser123', is_active=True
        )
        self.user.set_password('useruser123')
        self.user.save()

    def test_has_not_access(self):
        self.client.login(username='user', password='useruser123')
        response = self.client.get(
            reverse(
                'contest:contest-add-results',
                kwargs={'contest_id': self.contest.id}
            )
        )
        self.assertEqual(response.status_code, 302)
        url = '/'.format(
            reverse(
                'contest:contest-add-results',
                kwargs={'contest_id': self.contest.pk}
            )
        )
        self.assertEqual(
            response.url,
            url.format(reverse('contest:home'))
        )

    def test_has_access(self):
        self.client.login(username='admin', password='Password')
        response = self.client.get(
            reverse(
                'contest:contest-add-results',
                kwargs={'contest_id': self.contest.id}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_post_without_access(self):
        self.client.login(username='user', password='useruser123')
        response = self.client.post(
            reverse(
                'contest:contest-add-results',
                kwargs={'contest_id': self.contest.id}
            ),
            data={
                'results': 'Wyniki',
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        contest = Contest.objects.get(pk=self.contest.id)
        self.assertEqual(contest.results, '')

    def test_post_success(self):
        self.client.login(username='admin', password='Password')
        response = self.client.post(
            reverse(
                'contest:contest-add-results',
                kwargs={'contest_id': self.contest.id}
            ),
            data={
                'results': 'Wyniki',
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        contest = Contest.objects.get(pk=self.contest.id)
        self.assertEqual(contest.results, 'Wyniki')


class ManageContestViewTestCase(TestCase):
    def setUp(self):
        self.admin = RushUser.objects.create_superuser(
            email='xyz@xyz.pl', username='admin', password='Password'
        )
        self.contest = Contest.objects.create(
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=1997, highest_year=2000,
            description='Opis', deadline=make_aware(datetime(2008, 11, 20)),
            created_by=self.admin
        )
        self.client.login(username='admin', password='Password')

    def test_get_msg_without_contestants(self):
        response = self.client.get(
            reverse(
                'contest:contest-manage',
                kwargs={'contest_id': self.contest.id}
            ),
        )
        self.assertEqual(
            response.context['msg'],
            'Zawodnicy nie zostali jeszcze dodani.'
        )

    def test_get_contestants(self):
        self.contestant = Contestant.objects.create(
            moderator=self.admin, first_name='Adam', last_name='Nowak',
            gender='M', year_of_birth=2002, school='S', styles=['M50', 'Z100'],
            contest=self.contest
        )
        self.contestants = [self.contestant]
        response = self.client.get(
            reverse(
                'contest:contest-manage',
                kwargs={'contest_id': self.contest.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['contestants'][0],
            self.contestants[0]
        )
        self.assertEqual(
            response.context['msg'],
            ''
        )


class ContestEditViewTestCase(TestCase):
    def setUp(self):
        self.admin = RushUser.objects.create_superuser(
            email='xyz@xyz.pl', username='admin', password='Password'
        )
        self.contest = Contest.objects.create(
            name='abc',
            date=make_aware(datetime(2008, 12, 31)),
            place='Szkoła', lowest_year=11, highest_year=16,
            styles=',D25,G50,K200,Z100',
            description='Opis', deadline=make_aware(datetime(2008, 11, 20)),
            created_by=self.admin
        )
        self.client.login(username='admin', password='Password')

    def test_get(self):
        response = self.client.get(
            reverse(
                'contest:contest-edit',
                kwargs={'contest_id': self.contest.id}
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], ContestForm))
        self.assertEqual(
            response.context['form'].initial['lowest_year'], 11
        )
        self.assertEqual(
            response.context['form'].initial['highest_year'], 16
        )
        self.assertEqual(
            response.context['form'].initial['description'], 'Opis'
        )
        self.assertEqual(response.context['form'].initial['place'], 'Szkoła')

    def test_post(self):
        response = self.client.post(
            reverse(
                'contest:contest-edit',
                kwargs={'contest_id': self.contest.id}
            ),
            data={
                'lowest_year': 11, 'highest_year': 16,
                'description': '', 'place': 'Piła',
                'styles': ',D25,G50,K200,Z100',
                'organization': 'szkoła',
            }
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context['form'].cleaned_data['description'], ''
        )
        self.assertEqual(
            response.context['form'].cleaned_data['place'], 'Piła'
        )


class ContestAddTestCase(TestCase):
    def setUp(self):
        self.user_1 = RushUser.objects.create_user(
            email='d@d.pl', is_active=True, username='wrong',
            password='pass12', organization_name='plywanie'
        )
        self.user_2 = RushUser.objects.create_user(
            email='c@c.pl', is_active=True, username='right',
            password='pass12', organization_name='basen'
        )
        self.user_1.groups.add(Group.objects.get(name='Moderators'))
        self.user_2.groups.add(Group.objects.get(name='Moderators'))
        self.user_2.user_permissions.add(
            Permission.objects.get(name='Can add contest')
        )
        self.files = {
            'file1': SimpleUploadedFile(
                'file.mp4', b'file_content', content_type='media/mp4'
            ),
            'file2': SimpleUploadedFile(
                'file.doc', b'file_content', content_type='media/mp4'
            ),
            'file3': SimpleUploadedFile(
                'file.doc', b'', content_type="media/mp4"
            )
        }
        self.form_data = {
            'name': 'Wodnik',
            'date': '31.12.2100 16:00',
            'place': 'Majorka',
            'deadline': '29.12.2100 23:59',
            'lowest_year': 1999,
            'highest_year': 2002,
            'description': 'Zapraszamy na zawody!',
            'organization': self.user_1.unit,
            'styles': ',D25,G50,K200,Z100',
            'file1': '',
            'file2': '',
            'file3': ''
        }

    def test_has_access(self):
        self.client.login(username='wrong', password='pass12')
        response = self.client.get(reverse('contest:contest-add'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            '{}/?next=/zawody/dodaj'.format(reverse('contest:login'))
        )

        self.client.login(username='right', password='pass12')
        response = self.client.get(reverse('contest:contest-add'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['form'], ContestForm))

    def test_post_success(self):
        self.client.login(username='right', password='pass12')
        self.form_data['file2'] = self.files['file2']
        response = self.client.post(
            reverse('contest:contest-add'),
            data=self.form_data, file_data=self.files['file2']
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['message'],
            'Dziękujemy! Możesz teraz dodać zawodników.'
        )
        self.assertTrue(Contest.objects.filter(place='Majorka').exists())

    def test_post_errors(self):
        self.client.login(username='right', password='pass12')
        self.form_data['file1'] = self.files['file1']
        self.form_data['file3'] = self.files['file3']
        response = self.client.post(
            reverse('contest:contest-add'),
            data=self.form_data, file_data=self.files
        )
        self.assertEqual(
            response.context['form'].errors,
            {
                u'file3': [u'Przesłany plik jest pusty.'],
                u'file1':
                [
                    u'Niedozwolony format pliku. Obsługiwane rozszerzenia: '
                    '.pdf, .doc, .docx, .ods, .xls'
                ]
            }
        )
        self.form_data['deadline'] = '01.04.2200 16:00'
        response = self.client.post(
            reverse('contest:contest-add'), data=self.form_data
        )
        self.assertEqual(
            response.context['form'].errors['deadline'],
            [
                'Ostateczny termin dodawania zawodników nie może być później '
                'niż data zawodów.'
            ]
        )
        self.form_data['lowest_year'] = 2016
        self.form_data['date'] = '02.04.2016 16:00'
        self.form_data['deadline'] = '01.04.2016 16:00'
        response = self.client.post(
            reverse('contest:contest-add'), data=self.form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].errors['date'],
            ['Data zawodów nie może być wcześniejsza niż dzień dzisiejszy.']
        )
        self.assertEqual(
            response.context['form'].errors['deadline'],
            ['Termin dodawania zwodników musi być dłuższy niż podana data.']
        )
        self.assertEqual(
            response.context['form'].errors['highest_year'],
            [
                'Przedział wiekowy jest niepoprawny. '
                'Popraw wartości i spróbuj ponownie.'
            ]
        )
        self.form_data['date'] = '02.03.2011 16:00'
        self.form_data['deadline'] = '01.09.2016 16:00'

        response = self.client.post(
            reverse('contest:contest-add'), data=self.form_data
        )
        self.assertEqual(
            response.context['form'].errors['date'],
            ['Data zawodów nie może być wcześniejsza niż dzień dzisiejszy.']
        )
        self.form_data['date'] = '02.09.2016 16:00'
        self.form_data['deadline'] = '01.09.2011 16:00'

        response = self.client.post(
            reverse('contest:contest-add'), data=self.form_data
        )
        self.assertEqual(
            response.context['form'].errors['deadline'],
            ['Termin dodawania zwodników musi być dłuższy niż podana data.']
        )


class CompletedContestViewTestCase(TestCase):
    fixtures = ['contests.json', 'users.json']

    def setUp(self):
        self.contest = Contest.objects.get(pk=1)
        self.user = RushUser.objects.get(username='login321')
        self.user.set_password('password123')
        self.user.save()
        self.client.login(username='login321', password='password123')

    def test_valid_details(self):
        response = self.client.get(
            reverse('contest:completed-contest', kwargs={'contest_id': 999})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['msg'], 'Nie znaleziono konkursu.')
        response = self.client.get(
            reverse('contest:completed-contest', kwargs={'contest_id': 1})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['contest'], self.contest)


class ErrorViewTest(TestCase):
    def test_404_error(self):
        self.assertTrue(urls.handler404.endswith('.page_not_found'))
        response = self.client.get('/invalid_url/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.context['email'], settings.SUPPORT_EMAIL)

    def test_400_error(self):
        self.assertTrue(urls.handler400.endswith('.bad_request'))
        request = RequestFactory().get('/')
        response = bad_request(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(settings.SUPPORT_EMAIL, response.content)

    def test_403_error(self):
        self.assertTrue(urls.handler403.endswith('.permission_denied'))
        request = RequestFactory().get('/')
        response = permission_denied(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(settings.SUPPORT_EMAIL, response.content)

    def test_500_error(self):
        self.assertTrue(urls.handler500.endswith('.server_error'))
        request = RequestFactory().get('/')
        response = server_error(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(settings.SUPPORT_EMAIL, response.content)

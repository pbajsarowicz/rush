from django.test import TestCase
from django.contrib.auth import authenticate
from contest.models import RushUser
from contest.forms import LoginForm


class UserMethodTests(TestCase):
    def setUp(self):
        q = RushUser.objects.create_user('xyz@xyz.pl', 'Name', 'Last Name',
                                         'School', 'Address', 'Password')
        q.save()

    def test_authenticate(self):
        """
        Checking if authenticate() returns good values depending
        on input. In this case: correct data, incorrect, empty.

        """
        first = RushUser.objects.get(email='xyz@xyz.pl')
        self.assertEqual(authenticate(
            email='xyz@xyz.pl',
            password='Password'), first)  # auth returns object itself
        self.assertEqual(authenticate(
            email='xyz@xyz.pl',
            password='random_pass'), None)
        self.assertEqual(authenticate(
            email='example@example.pl',
            password='qwerty'), None)
        self.assertEqual(authenticate(email='', password=''), None)

    def test_login_form(self):
        """
        Checking if form is valid for correct data and invalid for
        wrong data or inactive user
        """
        self.assertEqual(list(LoginForm.base_fields), ['username', 'password'])

        form_data = {'username': 'xyz@xyz.pl', 'password': 'wrong_password'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
                         [u'Wprowad\u017a poprawny adres email oraz has'
                          u'\u0142o. Uwaga: wielko\u015b\u0107 '
                          u'liter ma znaczenie.'])

        form_data = {'username': 'xyz@xyz.pl', 'password': 'Password'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'],
                         [u'Konto nie zosta\u0142o aktywowane'])

        tmp = RushUser.objects.get(email='xyz@xyz.pl')
        tmp.is_active = True
        tmp.save()
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

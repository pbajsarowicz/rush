# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import json

from django.test import TestCase

from contest.models import RushUser
from contest.templatetags.to_json import (
    DatetimeEncoder,
    to_json,
)


class ToJSONTestCase(TestCase):

    def setUp(self):
        self.user = RushUser(
            email='test@user.pl', first_name='Test', last_name='Anonymous',
            is_active=True
        )
        self.user.set_password('password123')
        self.user.save()

    def test_datetime_encoder(self):
        encoder = DatetimeEncoder()
        example_datetime = datetime.datetime(day=1, month=1, year=2000)
        encoded_datetime = encoder.default(example_datetime)
        self.assertEqual(encoded_datetime, '01-01-2000 00:00:00')

        example_date = datetime.date(day=1, month=1, year=2000)
        encoded_date = encoder.default(example_date)
        self.assertEqual(encoded_date, '01-01-2000')

        example_date = 'Wrong format'
        self.assertRaises(TypeError, encoder.default, example_date)

    def test_to_json(self):
        result = to_json(self.user)
        result_json = json.loads(result)
        result_json.pop('password')
        result_json.pop('id')

        self.assertEqual(
            result_json,
            {
                'content_type': None,
                'email': 'test@user.pl',
                'first_name': 'Test',
                'groups': [],
                'is_active': True,
                'is_admin': False,
                'is_superuser': False,
                'last_login': None,
                'last_name': 'Anonymous',
                'object_id': None,
                'organization_address': '',
                'organization_name': '',
                'user_permissions': [],
                'username': ''
            }
        )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from contest.models import School
from contest.utils import AdminUtils


class UnitAdminMixinTestCase(TestCase):
    fixtures = ['contest/fixtures/schools.json']

    def test_get_options(self):
        active_content_type = ContentType.objects.get_for_model(School)
        options = AdminUtils.get_options(
            School, 'Szkoła', 1, active_content_type
        )
        self.assertEqual(
            options,
            [
                '<option value="2_school" >'
                '[Szko\u0142a] Klub wodnika</option>',
                '<option value="1_school" selected>'
                '[Szko\u0142a] ZSP1 w Pile</option>'
            ]
        )

    def test_get_unit_id_and_type(self):
        expected_content_type = ContentType.objects.get_for_model(School)

        self.assertEqual(
            ('1', expected_content_type,),
            AdminUtils.get_unit_id_and_type('1_school')
        )

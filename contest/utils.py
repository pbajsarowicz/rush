# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html


class AdminUtils(object):

    @staticmethod
    def get_options(model, prefix, active_object_id, active_content_type):
        options = []
        content_type = ContentType.objects.get_for_model(model)

        for organization in model.objects.all().order_by('name'):
            selected = (
                organization.id == active_object_id and
                content_type == active_content_type
            )
            options.append(format_html(
                '<option value="{}_{}" {}>[{}] {}</option>',
                organization.id, content_type,
                'selected' if selected else '',
                prefix, organization.name
            ))

        return options

    @staticmethod
    def get_unit_id_and_type(unit):
        object_id, content_type = unit.split('_')
        content_type = ContentType.objects.get(model=content_type)

        return object_id, content_type

admin_utils = AdminUtils()

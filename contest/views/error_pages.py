# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError
)
from django.template import loader


def bad_request(request):
    template = loader.get_template('error.html')
    body = template.render({'email': settings.SUPPORT_EMAIL}, request)
    return HttpResponseBadRequest(body)


def permission_denied(request):
    template = loader.get_template('error.html')
    body = template.render({'email': settings.SUPPORT_EMAIL}, request)
    return HttpResponseForbidden(body)


def page_not_found(request):
    template = loader.get_template('error.html')
    body = template.render({'email': settings.SUPPORT_EMAIL}, request)
    return HttpResponseNotFound(body)


def server_error(request):
    template = loader.get_template('error.html')
    body = template.render({'email': settings.SUPPORT_EMAIL}, request)
    return HttpResponseServerError(body)

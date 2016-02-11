# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    View for main page.
    """
    template_name = 'contest/home.html'

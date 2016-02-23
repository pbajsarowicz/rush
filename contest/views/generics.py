# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import formset_factory
from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    View,
)

from contest.forms import ContestantForm


class HomeView(TemplateView):
    """
    View for main page.
    """
    template_name = 'contest/home.html'


class ContestantAddView(View):
    """
    View for contestant assigning.
    """
    formset_class = formset_factory(ContestantForm)
    template_name = 'contest/contestant_add.html'

    def get(self, request, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        formset = self.formset_class()

        return render(request, self.template_name, {'formset': formset})

    def post(self, request, *args, **kwargs):
        """
        Create a contestant.
        """
        formset = self.formset_class(request.POST)

        if formset.is_valid():
            for form in formset:
                contestant = form.save(commit=False)
                contestant.moderator = request.user
                contestant.save()

            return render(
                request, self.template_name, {'message': 'Dodano zawodników.'}
            )

        return render(request, self.template_name, {'formset': formset})

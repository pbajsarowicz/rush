# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    form_class = ContestantForm
    template_name = 'contest/contestant_add.html'

    def get(self, request, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Create a contestant.
        """
        form = self.form_class(request.POST)

        if form.is_valid():
            contestant = form.save(commit=False)
            contestant.moderator = request.user
            contestant.save()

            return render(
                request, 'contest/contestant_confirmation.html',
                {'message': 'Dodano zawodnika.'}
            )

        return render(request, self.template_name, {'form': form})

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.utils import timezone
from django.views.generic import (
    TemplateView,
    View,
)

from contest.forms import ContestantForm
from contest.models import Contest


class HomeView(TemplateView):
    """
    View for main page.
    """
    template_name = 'contest/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['upcoming'] = Contest.objects.filter(date__gte=timezone.now())
        context['completed'] = Contest.objects.filter(date__lt=timezone.now())

        return context


class ContestantAddView(View):
    """
    View for contestant assigning.
    """
    form_class = ContestantForm
    template_name = 'contest/contestant_add.html'

    @staticmethod
    def _get_message(contest=None):
        """
        Returns a message basing on given contest.
        """
        if not contest:
            return 'Takie zawody nie istnieją.'
        elif not contest.is_submitting_open and contest.is_future:
            return 'Czas na dodawanie zawodników już minął.'
        return 'Zawody się już skończyły.'

    def get(self, request, id, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        form = self.form_class(contest_id=id)
        try:
            contest = Contest.objects.get(pk=id)
        except Contest.DoesNotExist:
            return render(
                request, self.template_name, {'message': self._get_message()}
            )

        if timezone.now() > contest.deadline:
            return render(
                request,
                self.template_name,
                {'message': self._get_message(contest)}
            )
        return render(
            request, self.template_name, {'form': form, 'name': contest}
        )

    def post(self, request, id, *args, **kwargs):
        """
        Create a contestant.
        """
        form = self.form_class(request.POST, contest_id=id)
        try:
            contest = Contest.objects.get(pk=id)
        except Contest.DoesNotExist:
            return render(
                request, self.template_name, {'message': self._get_message()}
            )
        if form.is_valid():
            contestant = form.save(commit=False)
            contestant.moderator = request.user
            contestant.contest = contest
            contestant.save()
            return render(
                request, self.template_name,
                {'message': 'Dodano zawodnika.'}
            )
        return render(request, self.template_name, {'form': form})

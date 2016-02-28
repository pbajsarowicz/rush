# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import formset_factory
from django.shortcuts import render
from django.utils import timezone
from django.utils.functional import curry
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

    @staticmethod
    def get_formset(contest_id, data=None):
        """
        Returns formset of `ContestantForm` forms.
        """
        formset_class = formset_factory(ContestantForm, extra=1)
        formset_class.form = staticmethod(
            curry(ContestantForm, contest_id=contest_id)
        )
        return formset_class(data) if data else formset_class()

    def get(self, request, id, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        formset = self.get_formset(id)

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
            request, self.template_name, {'formset': formset, 'name': contest}
        )

    def post(self, request, id, *args, **kwargs):
        """
        Create a contestant.
        """
        formset = self.get_formset(id, request.POST)

        try:
            contest = Contest.objects.get(pk=id)
        except Contest.DoesNotExist:
            return render(
                request, self.template_name, {'message': self._get_message()}
            )

        if formset.is_valid():
            for form in formset:
                contestant = form.save(commit=False)
                contestant.moderator = request.user
                contestant.contest = contest
                contestant.save()

            msg = (
                'Dziękujemy! Potwierdzenie zapisów zostało wysłane na email '
                'podany przy rejestracji. Życzymy powodzenia.'
            )

            return render(request, self.template_name, {'message': msg})

        return render(request, self.template_name, {'formset': formset})

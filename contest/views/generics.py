# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

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
        contests = Contest.objects.all()
        upcoming = [obj for obj in contests if obj.date > timezone.now()]
        completed = [obj for obj in contests if obj.date < timezone.now()]
        context = {
            'upcoming': upcoming,
            'completed': completed,
        }

        return context


class ContestantAddView(View):
    """
    View for contestant assigning.
    """
    form_class = ContestantForm
    template_name = 'contest/contestant_add.html'

    @staticmethod
    def _check_contest(contest_id):
        """
        For given contest pk:
        returns contest object or string containing error.
        """
        try:
            contest = Contest.objects.get(pk=contest_id)
        except Contest.DoesNotExist:
            return 'Takie zawody nie istnieją.'
        if timezone.now() < contest.deadline:
            return contest
        elif contest.deadline < timezone.now() < contest.date:
            return 'Czas na dodawanie zawodników już minął.'
        else:
            return 'Zawody się już skończyły.'

    def get(self, request, id, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        form = self.form_class()
        contest = self._check_contest(id)
        if not isinstance(contest, Contest):
            return render(
                request, self.template_name, {'message': contest}
            )

        name = 'Konkurs: {}'.format(contest)
        return render(
            request,
            self.template_name,
            {'form': form, 'name': name}
        )

    def post(self, request, id, *args, **kwargs):
        """
        Create a contestant.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            contestant = form.save(commit=False)
            contestant.moderator = request.user
            contest = self._check_contest(id)
            if not isinstance(contest, Contest):
                return render(
                    request, self.template_name, {'message': contest}
                )
            ages = map(int, re.findall('\d{2}', contest.for_who))
            if not(ages[0] <= contestant.age <= ages[1]):
                return render(
                    request,
                    self.template_name,
                    {
                        'message': 'Zawodnik nie mieści się w '
                                   'wymaganym przedziale wiekowym.'
                    }
                )
            contestant.contest = contest
            contestant.save()
            return render(
                request, self.template_name,
                {'message': 'Dodano zawodnika.'}
            )
        return render(request, self.template_name, {'form': form})

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMessage
from django.forms import formset_factory
from django.shortcuts import(
    render,
    redirect,
)
from django.template import loader
from django.utils import timezone
from django.utils.functional import curry
from django.views.generic import (
    TemplateView,
    View,
)

from contest.forms import ContestantForm
from contest.models import (
    Contest,
    Contestant,
)


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

    @staticmethod
    def send_email_with_contestant(contestants, email, *args, **kwargs):
        """
        Sends an email with a list contestants
        """
        text = loader.render_to_string(
            'email/contestant_add.html', {'contestants': contestants},
        )
        msg = EmailMessage(
            'Potwierdzenie dodania zawodników',
            text,
            settings.SUPPORT_EMAIL,
            [email],
        )
        msg.content_subtype = 'html'
        msg.send()

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
            contestants = []
            for form in formset:
                contestant = form.save(commit=False)
                contestant.moderator = request.user
                contestant.contest = contest
                contestant.save()
                contestants.append(contestant)
            self.send_email_with_contestant(contestants, request.user.email)

            msg = (
                'Dziękujemy! Potwierdzenie zapisów zostało wysłane na email '
                'podany przy rejestracji. Życzymy powodzenia.'
            )

            return render(request, self.template_name, {'message': msg})

        return render(request, self.template_name, {'formset': formset})


class ContestantListView(View):
    """
    View with list of added contestants.
    """
    template_name = 'contest/contestant_list.html'

    def get(self, request, contest_id, *args, **kwargs):
        """
        Get contestant data.
        """
        contestants = Contestant.objects.filter(
            contest=contest_id, moderator=request.user,
        )
        if contestants:
            return render(
                request, self.template_name, {'contestants': contestants}
            )
        else:
            return render(
                request, self.template_name,
                {'msg': 'Nie dodałeś zawodników do tych zawodów.'},
            )


class EditContestantView(View):
    """
    Edit contestant page.
    """

    template_name = 'contest/contestant_edit.html'
    form_class = ContestantForm
    data = {}

    def get(self, request, contestant_id, *args, **kwargs):
        """
        Return form with filled fields.
        """
        contestant = Contestant.objects.get(id=contestant_id)

        self.data = {
            'first_name': contestant.first_name,
            'last_name': contestant.last_name,
            'gender': contestant.gender,
            'age': contestant.age,
            'school': contestant.school,
            'styles_distances': contestant.styles_distances,
        }
        form = self.form_class(
            initial=self.data, contest_id=contestant.contest.id,
        )

        if not contestant.moderator == request.user:
            return render(
                request, self.template_name,
                {'msg': 'Nie możesz edytować tego zawodnika.'},
            )
        return render(
            request, self.template_name,
            {'contestant': contestant, 'form': form},
        )

    def post(self, request, contestant_id, *args, **kwargs):
        """
        Submit contestant data.
        """
        contestant = Contestant.objects.get(id=contestant_id)
        form = self.form_class(
            request.POST, instance=contestant, contest_id=contestant.contest.id
        )
        if form.has_changed():
            if form.is_valid():
                form.save()
                return redirect(
                    'contest:contestant-list', contest_id=contestant.contest.id
                )
            else:
                return render(
                    request, self.template_name,
                    {'contestant': contestant, 'form': form},
                )
        else:
            return redirect(
                'contest:contestant-list',
                contest_id=contestant.contest.id,
            )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
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

from contest.models import (
    Contest,
    Contestant,
)
from contest.forms import (
    ContestantForm,
    ContestForm,
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
    def get_formset(contest_id, user, data=None):
        """
        Returns formset of `ContestantForm` forms.
        """
        formset_class = formset_factory(ContestantForm, extra=1)
        formset_class.form = staticmethod(
            curry(ContestantForm, contest_id=contest_id, user=user)
        )
        return formset_class(data) if data else formset_class()

    @staticmethod
    def send_email_with_contestant(contestants, email, link, *args, **kwargs):
        """
        Sends an email with a list contestants
        """
        text = loader.render_to_string(
            'email/contestant_add.html', {
                'contestants': contestants, 'link': link
            },
        )
        msg = EmailMessage(
            'Potwierdzenie dodania zawodników',
            text,
            settings.SUPPORT_EMAIL,
            [email],
        )
        msg.content_subtype = 'html'
        msg.send()

    def get(self, request, contest_id, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        user = request.user
        organization = request.user.unit
        formset = self.get_formset(contest_id, user)

        try:
            contest = Contest.objects.get(pk=contest_id)
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
            request, self.template_name, {
                'formset': formset,
                'name': contest,
                'organization': organization,
            }
        )

    def post(self, request, contest_id, *args, **kwargs):
        """
        Create a contestant.
        """
        formset = self.get_formset(contest_id, request.user, request.POST)

        try:
            contest = Contest.objects.get(pk=contest_id)
        except Contest.DoesNotExist:
            return render(
                request, self.template_name, {'message': self._get_message()}
            )

        link = 'http://{}{}'.format(
            request.get_host(),
            reverse(
                'contest:contestant-list', kwargs={'contest_id': contest_id}
            )
        )

        if formset.is_valid():
            contestants = []
            for form in formset:
                contestant = form.save(commit=False)
                contestant.moderator = request.user
                contestant.contest = contest
                contestant.save()
                contestants.append(contestant)

            self.send_email_with_contestant(
                contestants, request.user.email, link,
            )

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
        Get contestants data.
        """
        contest = Contest.objects.get(pk=contest_id)
        if request.user.object_id == contest.object_id:
            contestants = Contestant.objects.filter(contest=contest_id,)
        else:
            contestants = Contestant.objects.filter(
                contest=contest_id, moderator=request.user,
            )

        if contestants:
            return render(
                request, self.template_name, {'contestants': contestants}
            )
        if request.user.object_id == contest.object_id:
            return render(
                request, self.template_name,
                {'msg': 'Nie zostali jeszcze dodani zawodnicy.'},
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

    def get(self, request, contestant_id, *args, **kwargs):
        """
        Return form with filled fields.
        """
        contestant = Contestant.objects.get(id=contestant_id)
        user = request.user

        form = self.form_class(
            instance=contestant,
            contest_id=contestant.contest.id,
            user=user
        )

        if not contestant.moderator == request.user:
            return render(
                request, self.template_name,
                {'msg': 'Nie możesz edytować tego zawodnika.'},
            )
        return render(
            request, self.template_name,
            {'contestant': contestant, 'form': form, 'user': user},
        )

    def post(self, request, contestant_id, *args, **kwargs):
        """
        Submit contestant data.
        """
        contestant = Contestant.objects.get(id=contestant_id)
        form = self.form_class(
            request.POST,
            user=request.user,
            instance=contestant,
            contest_id=contestant.contest.id
        )
        if form.has_changed():
            if form.is_valid():
                form.save()
                return redirect(
                    'contest:contestant-list', contest_id=contestant.contest.id
                )
            return render(
                request, self.template_name,
                {'contestant': contestant, 'form': form},
            )
        return redirect(
            'contest:contestant-list',
            contest_id=contestant.contest.id,
        )


class ContestAddView(PermissionRequiredMixin, View):
    """
    View for adding contests.
    """
    permission_required = 'contest.add_contest'
    template_name = 'contest/contest_add.html'
    form_class = ContestForm

    def get(self, request):
        """
        Return clear form.
        """
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Create new Contest.
        """
        form = self.form_class(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            msg = 'Dziękujemy! Możesz teraz dodać zawodników.'
            return render(request, self.template_name, {'message': msg})
        return render(request, self.template_name, {'form': form})

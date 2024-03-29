# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urljoin

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.forms import (
    formset_factory,
    inlineformset_factory,
)
from django.shortcuts import (
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
    Style,
    Distance,
    ContestantScore,
    RushUser,
)
from contest.forms import (
    ContestantForm,
    ContestForm,
    ContestResultsForm,
)


class HomeView(TemplateView):
    """
    View for main page.
    """
    template_name = 'contest/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['upcoming'] = Contest.objects.filter(
            date__gte=timezone.now()
        ).order_by('date')
        context['completed'] = Contest.objects.filter(
            date__lt=timezone.now()
        ).order_by('-date')

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

    def send_email_with_contestant(self, contestants, link, *args, **kwargs):
        """
        Sends an email with a list contestants
        """
        text = loader.render_to_string(
            'email/contestant_add.html', {
                'contestants': contestants,
                'link': link,
                'is_individual_contestant': (
                    self.request.user.is_individual_contestant
                ),
            },
        )
        subject = (
            'Potwierdzenie dodania zawodników'
            if not self.request.user.is_individual_contestant else
            'Potwierdzenie dodania do zawodów'
        )
        msg = EmailMessage(
            subject, text, settings.SUPPORT_EMAIL, [self.request.user.email],
        )
        msg.content_subtype = 'html'
        msg.send()

    def _can_sign_in(self, contest_id):
        return not (
            self.request.user.is_individual_contestant and
            Contestant.objects.filter(
                contest__pk=contest_id, moderator=self.request.user
            ).exists()
        )

    @staticmethod
    def _save_styles(raw_styles, contestant):
        for score in raw_styles.split(';'):
            score = score.split(',')
            style = Style.objects.get(name=score[0])
            distance = Distance.objects.get(value=score[1])
            time = int(score[2][:2]) * 60000 + int(score[2][3:5]) * 1000
            time += int(score[2][6:8]) * 10
            ContestantScore.objects.create(
                contestant=contestant, style=style, distance=distance,
                time_result=time
            )

    def get(self, request, contest_id, *args, **kwargs):
        """
        Return adding a contestant form on site.
        """
        if not self._can_sign_in(contest_id):
            return render(
                request,
                self.template_name,
                {'message': 'Jesteś już zapisany na ten konkurs'}
            )

        organization = request.user.unit
        formset = self.get_formset(contest_id, request.user)

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
                'styles': contest.styles,
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
                self._save_styles(form.cleaned_data['styles'], contestant)
                contestants.append(contestant)

            self.send_email_with_contestant(contestants, link)

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

    @staticmethod
    def _is_contest_organizer(request, contest):
        """
        Checks if a logged user calls for a list of contestans which attend to
        contest created by this user.
        """
        return request.user.object_id == contest.object_id

    @staticmethod
    def _get_contestants(is_contest_organizer, contest, request):
        """
        Returns a contestans queryset.
        """
        return (
            contest.contestant_set.all() if is_contest_organizer else
            contest.contestant_set.filter(moderator=request.user)
        )

    @staticmethod
    def _get_msg(is_contest_organizer, contestants=None):
        """
        Returns a message.
        """
        if not contestants:
            if is_contest_organizer:
                return 'Zawodnicy nie zostali jeszcze dodani.'
            return 'Nie dodałeś zawodników do tych zawodów.'
        return ''

    def get(self, request, contest_id, *args, **kwargs):
        """
        Get contestants data.
        """
        contest = Contest.objects.get(pk=contest_id)
        is_contest_organizer = self._is_contest_organizer(request, contest)
        contestants = self._get_contestants(
            is_contest_organizer, contest, request
        )
        msg = self._get_msg(is_contest_organizer, contestants)

        context = {
            'contest': contest,
            'contestants': contestants,
            'msg': msg,
        }

        return render(request, self.template_name, context)


class EditContestantView(View):
    """
    Edit contestant page.
    """
    template_name = 'contest/contestant_edit.html'
    form_class = ContestantForm
    ContestantFormset = inlineformset_factory(
        Contestant, ContestantScore,
        fields=('style', 'distance', 'time_result'),
        extra=0, can_delete=False
    )

    def get(self, request, contestant_id, *args, **kwargs):
        """
        Return form with filled fields.
        """
        contestant = Contestant.objects.get(id=contestant_id)

        user = request.user
        contest = contestant.contest
        form = self.form_class(
            instance=contestant,
            contest_id=contest.id,
            user=user,
        )

        if not contestant.moderator == request.user:
            return render(
                request, self.template_name,
                {'msg': 'Nie możesz edytować tego zawodnika.'},
            )
        return render(
            request,
            self.template_name,
            {
                'contestant': contestant,
                'formset': self.ContestantFormset(instance=contestant),
                'form': form,
                'user': user,
            },
        )

    def post(self, request, contestant_id, *args, **kwargs):
        """
        Submit contestant data.
        """
        contestant = Contestant.objects.get(id=contestant_id)
        contest = contestant.contest
        form = self.form_class(
            request.POST,
            user=request.user,
            instance=contestant,
            contest_id=contest.id
        )
        formset = self.ContestantFormset(request.POST, instance=contestant)
        valid = True
        if form.is_valid():
            form.save()
        else:
            valid = False
        if formset.has_changed():
            if formset.is_valid():
                for form in formset:
                    form.save()
            else:
                valid = False
        if valid:
            return redirect(
                'contest:contestant-list', contest_id=contest.id
            )
        return render(
            request,
            self.template_name,
            {
                'contestant': contestant,
                'form': form,
                'formset': formset
            },
        )


class ContestAddView(PermissionRequiredMixin, View):
    """
    View for adding contests.
    """
    permission_required = 'contest.add_contest'
    template_name = 'contest/contest_add.html'
    form_class = ContestForm

    @staticmethod
    def send_email_about_new_contest(
        contest, recipient_list, add_contestant_link, files_list, request,
        *args, **kwargs
    ):
        """
        Sends an email with a list contestants
        """
        cancel_notifications_link = urljoin(
            'http://{}'.format(request.get_host()),
            reverse('contest:cancel-notification')
        )
        body = loader.render_to_string(
            'email/new_contest_notification.html', {
                'link': cancel_notifications_link,
                'contest': contest,
                'add_contestant_link': add_contestant_link,
                'files_list': files_list
            },
        )
        msg = EmailMessage(
            subject='Stworzono nowe zawody',
            body=body,
            from_email=settings.SUPPORT_EMAIL,
            bcc=recipient_list,
        )
        msg.content_subtype = 'html'
        msg.send()

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
        form = self.form_class(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            contest = form.save()
            recipient_list = list(
                RushUser.objects.filter(
                    notifications=True, is_active=True
                ).exclude(
                    email=request.user.email
                ).values_list(
                    'email', flat=True
                )
            )
            add_contestant_link = 'http://{}{}'.format(
                request.get_host(),
                reverse(
                    'contest:contestant-add', kwargs={'contest_id': contest.pk}
                )
            )
            contest_files = contest.contestfiles_set.all()
            host = request.get_host()
            files_list = [
                {
                    'name': contest_file.name,
                    'url': 'http://{}{}'.format(
                        host, contest_file.contest_file.url
                    )
                } for contest_file in contest_files
            ]

            self.send_email_about_new_contest(
                contest, recipient_list, add_contestant_link, files_list,
                request
            )
            msg = 'Dziękujemy! Możesz teraz dodać zawodników.'

            return render(request, self.template_name, {'message': msg})
        return render(request, self.template_name, {'form': form})


class ContestResultsAddView(View):
    """
    View for adding contest results.
    """
    template_name = 'contest/add_results.html'
    form_class = ContestResultsForm

    @staticmethod
    def _is_contest_organizer(user, contest):
        """
        Checks if contest is created by this user.
        """
        return user == contest.created_by

    @staticmethod
    def _is_contest_moderator(user, contest):
        """
        Checks is a request user's organization matches contest's one and
        whether it's moderator or not.
        """
        return (
            user.is_moderator and
            user.content_type == contest.content_type and
            user.object_id == contest.object_id
        )

    def _can_add_result(self, user, contest):
        """
        Both a contest's creator and a moderator of an organization that
        belongs to the contest should be able to add results.
        """
        return (
            self._is_contest_organizer(user, contest) or
            self._is_contest_moderator(user, contest) or
            user.is_staff
        )

    def get(self, request, contest_id, *args, **kwargs):
        """
        Return clear form.
        """
        contest = Contest.objects.get(pk=contest_id)
        if self._can_add_result(request.user, contest) is False:
            return redirect('contest:home')
        form = self.form_class(instance=contest)
        return render(request, self.template_name, {'form': form})

    def post(self, request, contest_id, *args, **kwargs):
        """
        Save results.
        """
        contest = Contest.objects.get(pk=contest_id)
        if self._can_add_result(request.user, contest) is False:
            return redirect('contest:home')
        form = self.form_class(request.POST, instance=contest)
        if form.is_valid():
            form.save(commit=True)
            return redirect('contest:contest-results', contest_id=contest_id)
        return render(request, self.template_name, {'form': form})


class ContestResultsView(View):
    """
    Displays results.
    """
    template_name = 'contest/contest_results.html'

    @staticmethod
    def _get_results(contest_id, request):
        """
        Returns a results queryset.
        """
        contest = Contest.objects.get(pk=contest_id)
        return contest.results

    @staticmethod
    def _get_msg(results=None):
        """
        Returns a message.
        """
        if not results:
            return 'Nie dodano jeszcze wyników.'
        return ''

    def get(self, request, contest_id, *args, **kwargs):
        """
        Get results data.
        """
        contest = Contest.objects.get(pk=contest_id)
        results = self._get_results(
            contest_id, request
        )
        msg = self._get_msg(results)

        context = {
            'contest': contest,
            'results': results,
            'msg': msg,
        }
        return render(request, self.template_name, context)


class CompletedContestView(View):
    """
    Completed contest details page.
    """
    template_name = 'contest/completed_contest.html'

    def get(self, request, contest_id):
        """
        Return contest details.
        """
        try:
            contest = Contest.objects.get(pk=contest_id)
        except Contest.DoesNotExist:
            return render(
                request,
                self.template_name,
                {'msg': 'Nie znaleziono konkursu.'}
            )
        return render(request, self.template_name, {'contest': contest})


class ManageContestView(View):
    """
    Organizer's panel.
    """
    template_name = 'contest/organizer_panel.html'

    @staticmethod
    def _get_contestants(contest, request):
        """
        Returns a contestans queryset.
        """
        return contest.contestant_set.all()

    @staticmethod
    def _get_msg(contestants=None):
        """
        Returns a message.
        """
        if not contestants:
            return 'Zawodnicy nie zostali jeszcze dodani.'
        return ''

    def get(self, request, contest_id, *args, **kwargs):
        """
        Return contest details.
        """
        contest = Contest.objects.get(pk=contest_id)
        contestants = self._get_contestants(contest, request)
        msg = self._get_msg(contestants)
        context = {
            'contest': contest,
            'contestants': contestants,
            'msg': msg,
        }
        return render(request, self.template_name, context)


class ContestEditView(View):
    permission_required = 'contest.add_contest'
    template_name = 'contest/contest_edit.html'
    form_class = ContestForm

    def get(self, request, contest_id, *args, **kwargs):
        """
        Return clear form.
        """
        contest = Contest.objects.get(id=contest_id)
        form = self.form_class(user=request.user, instance=contest)
        return render(
            request, self.template_name, {'form': form, 'contest': contest}
        )

    def post(self, request, contest_id, *args, **kwargs):
        """
        Edit Contest.
        """
        contest = Contest.objects.get(id=contest_id)
        form = self.form_class(
            request.POST, request.FILES, instance=contest, user=request.user
        )
        if form.is_valid():
            form = form.save()
            msg = 'Zawody zostały edytowane.'
            return render(request, self.template_name, {'message': msg})
        return render(request, self.template_name, {'form': form})

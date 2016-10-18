# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic import View

from contest.models import RushUser


class AccountsView(PermissionRequiredMixin, View):
    """
    Special view for Rush's admin. Displays users whose one can
    confirm or cancel, and fields 'imie' and 'nazwisko' RushUser.
    """
    template_name = 'contest/accounts.html'
    permission_required = 'is_staff'

    def get(self, request, user_id):
        """
        Transfer RushUser model and render pages 'administratorzy/konta'.
        """
        users = RushUser.objects.filter(is_active=False)

        return render(request, self.template_name, {'users': users})

    def post(self, request, user_id):
        """
        Creates a user, with temporary password.
        """
        try:
            user = RushUser.objects.get(pk=user_id)
            user.activate()
            user.send_reset_password_email(request, True)
        except RushUser.DoesNotExist:
            return HttpResponse(status=500)
        return HttpResponse(status=201)

    def delete(self, request, user_id):
        """
        Deletes a user.
        """
        try:
            user = RushUser.objects.get(pk=user_id)
            self.send_rejection_email(user.email)
            user.delete()
        except RushUser.DoesNotExist:
            return HttpResponse(status=500)
        return HttpResponse(status=204)

    @staticmethod
    def send_rejection_email(email):
        """
        Send a email notification about removal user.
        """
        support = settings.SUPPORT_EMAIL
        template = ('email/rejection_account.html',)
        text = loader.render_to_string(template, {'email': support})
        msg = EmailMessage(
            'Podanie o konto odrzucone', text, support, [email]
        )
        msg.content_subtype = 'html'
        msg.send()


class CancelNotificationsView(View):
    """
    Special link, that canceled notifications.
    """
    template_name = 'contest/cancel_notification.html'

    def get(self, request):
        """
        Cancel notifications.
        """
        try:
            request.user.cancel_notifications()
        except RushUser.DoesNotExist:
            return render(
                request, self.template_name, {
                    'msg': """Nie udało się wyłączyć powiadomień.
                     Spróbuj ponownie. Jeśli problem się pojawi
                     skontaktuj się z nami:""", 'email': settings.SUPPORT_EMAIL
                }
            )
        return render(
            request, self.template_name,
            {'msg': 'Powiadomienia odnośnie nowych zawodów zostały wyłączone.'}
        )

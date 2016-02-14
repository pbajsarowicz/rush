# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from contest.models import RushUser


class AccountsView(View):
    """
    Special view for Rush's admin. Displays users whose one can
    confirm or cancel, and fields 'imie' and 'nazwisko' RushUser.
    """
    template_name = 'contest/accounts.html'
    users = RushUser.objects.filter(is_active=False)

    def get(self, request, user_id):
        """
        Transfer RushUser model and render pages 'administratorzy/konta'.
        """
        return render(request, self.template_name, {'users': self.users})

    def post(self, request, user_id):
        """
        Creates a user, with temporary password.
        """
        try:
            user = RushUser.objects.get(pk=user_id)
            user.activate()
            user.send_reset_email(request)
        except RushUser.DoesNotExist:
            return HttpResponse(status=500)
        return HttpResponse(status=201)

    def delete(self, request, user_id):
        """
        Deletes a user.
        """
        try:
            RushUser.objects.get(pk=user_id).delete()
        except RushUser.DoesNotExist:
            return HttpResponse(status=500)
        return HttpResponse(status=204)

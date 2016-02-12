# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import (
    TemplateView,
    View,
)
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import (
    redirect,
    render,
)
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from contest.forms import (
    LoginForm,
    RegistrationForm,
    SettingPasswordForm,
    ContestantForm,
)
from contest.models import RushUser


class HomeView(TemplateView):
    """
    View for main page.
    """
    template_name = 'contest/home.html'


class RegisterView(View):
    """
    View for user registration.
    """
    form_class = RegistrationForm
    template_name = 'contest/register.html'

    def get(self, request, *args, **kwargs):
        """
        Return registration form on site.
        """
        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Send form and check validation.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(
                request, 'contest/confirmation.html',
                {'email': settings.SUPPORT_EMAIL}
            )
        else:
            return render(request, self.template_name, {'form': form})


class LoginView(View):
    """
    View for login page. Form is checking for correct input
    and also making sure user is activated.
    """
    form_class = LoginForm
    template_name = 'contest/login.html'

    def get(self, request):
        """
        Displaying clear LoginForm on page.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Log an user into app.
        """
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('contest:home')
        return render(request, self.template_name, {'form': form})


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


class SetPasswordView(View):
    """
    View for setting user's password.
    """
    form_class = SettingPasswordForm
    template_name = 'contest/set_password.html'

    @staticmethod
    def _get_user(uid):
        """
        Returns user for given uuid64
        """
        try:
            user_id = force_text(urlsafe_base64_decode(uid))
            user = RushUser.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, RushUser.DoesNotExist):
            user = None
        return user

    def get(self, request, uidb64=None, token=None):
        """
        Return clear form for setting password.
        """
        user = self._get_user(uidb64)

        if user and default_token_generator.check_token(user, token):
            form = self.form_class(user)
            return render(request, self.template_name, {'form': form})
        return redirect('contest:login')

    def post(self, request, uidb64=None, token=None):
        """
        Set user's password.
        """
        user = self._get_user(uidb64)

        if user and default_token_generator.check_token(user, token):
            form = self.form_class(user, data=request.POST)
            if form.is_valid():
                form.save()
                return render(
                    request, self.template_name,
                    {'message': 'Hasło ustawione, można się zalogować.'}
                )
        return render(request, self.template_name, {'form': form})



class AddContestantView(View):
    """
    View for  contestant assigning  .
    """
    form_class = ContestantForm
    template_name = 'contest/assign_contestant.html'

    def get(self, request, *args, **kwargs):
        """
        Return adding contestant form on site.
        """
        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Send, check validation and return adding page.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return render(
                request, self.template_name, {'form': self.form_class}
                )
        return render(request, self.template_name, {'form': form})

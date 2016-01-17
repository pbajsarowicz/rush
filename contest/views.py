# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import (
    TemplateView,
    View,
)
from django.contrib.auth import login
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
                request, self.template_name,
                {'success_message': 'Wysłano zapytanie o konto'}
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


class SetPasswordView(View):
    """
    View for setting user's password.
    """
    form_class = SettingPasswordForm
    template_name = 'contest/set_password.html'

    def get(self, request, uidb64=None, token=None):
        """
        Return clear form for setting password.
        """
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = RushUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, RushUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            form = self.form_class(user)
            return render(request, self.template_name, {'form': form})
        return redirect('contest:login')

    def post(self, request, uidb64=None, token=None):
        """
        Set user's password.
        """
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = RushUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, RushUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            form = self.form_class(user, data=request.POST)
            if form.is_valid():
                form.save()
                return render(
                    request, self.template_name,
                    {'message': 'Hasło ustawione, można się zalogować.'}
                )
        return render(request, self.template_name, {'form': form})

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

from contest.forms import (
    LoginForm,
    RegistrationForm,
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
        Displaying clear LoginForm on page without any errors.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Checking if form is valid (correct login, password, account
        activated). If everything is okay logs user in and redirects to home
        page, if not - returns form with errors.
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
    def get(self, request):
        """
        Transfer RushUser model and render pages 'administratorzy/konta'.
        """
        users = RushUser.objects.filter()
        return render(request, 'contest/accounts.html', {'users': users})

# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.contrib.auth.views import logout_then_login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from contest.models import RushUser
from contest.forms import LoginForm


class HomeView(TemplateView):
    """
    View for main page
    """
    template_name = 'contest/home.html'


class LoginView(TemplateView):
    """
    View for login page. Form is checking for correct input
    and also making sure user is activated.
    """
    template_name = 'contest/login.html'
    model = RushUser

    def get(self, request):
        form = LoginForm(None, None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(None, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect('/')
        else:
            return render(request, self.template_name, {'form': form})


def user_logout(request):
    """
    :param request:
    :return: logout_then_login(request)
    Logs user out and redirects him to login page automatically.
    """
    return logout_then_login(request)

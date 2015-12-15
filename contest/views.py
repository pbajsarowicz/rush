# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, View
from django.contrib.auth import login
from django.shortcuts import render, redirect

from contest.forms import LoginForm


class HomeView(TemplateView):
    """
    View for main page
    """
    template_name = 'contest/home.html'


class LoginView(View):
    """
    View for login page. Form is checking for correct input
    and also making sure user is activated.
    """

    form_class = LoginForm
    template_name = 'contest/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('contest:home')
        return render(request, self.template_name, {'form': form})

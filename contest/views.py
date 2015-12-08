# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .forms import RegistrationForm

from django.shortcuts import render

from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'contest/home.html'


def register(request):

    if request.method == "POST":
        form = RegistrationForm(request.POST, instance = regis)
        if form.is_valid():
            RegistrationForm = form.save(commit = False)
            RegistrationForm.save()
            return redirect('contest.views.HomeView')

    return render(request, 'contest/register.html', {'form': RegistrationForm})

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from django.shortcuts import render

from .forms import RegistrationForm


class HomeView(TemplateView):
    template_name = 'contest/home.html'

def register(request):
	form = RegistrationForm()
	if request.method == "POST":
		form = RegistrationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			new_user.save()
	else:
		form = RegistrationForm()

    return render(request, 'contest/register.html', {'form': form})


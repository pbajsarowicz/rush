# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from django.views.generic import View

from django.shortcuts import render

from django.http import HttpResponseRedirect

from contest.forms import RegistrationForm


class HomeView(TemplateView):
    template_name='contest/home.html'

class ThanksView(TemplateView):
    template_name='contest/thanks.html'


class RegisterView(View):

	def get(self, request):

		return render(request, 'contest/register.html',
		{'form': RegistrationForm}
		)

	def post(self, request):

		form = RegistrationForm(request.POST)
		if form.is_valid():

			tmp = form.save(commit = False)
			tmp.save()
		else:
			return render(request, 'contest/register.html',
			{'form': form}
			)

		return HttpResponseRedirect('/thanks')


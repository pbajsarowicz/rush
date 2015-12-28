# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import (
	TemplateView,
	View
)
from django.shortcuts import render
from django.http import HttpResponseRedirect

from contest.forms import RegistrationForm


class HomeView(TemplateView):
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

		return render(
			request, self.template_name, 
			{'form': form}
		)

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
			return render(
				request, self.template_name, {'form': form}
			)

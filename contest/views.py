# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render


class HomeView(TemplateView):
	template_name = 'contest/home.html'


def login_check(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/')
			else:
				return render(request, 'contest/login.html', {
					'warning': 'Konto nie zostało aktywowane'})
		else:
			return render(request, 'contest/login.html', {
				'warning': 'Złe dane logowania'})
	else:
		return render(request, 'contest/login.html')


def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')
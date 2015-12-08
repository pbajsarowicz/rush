# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from contest import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^register', views.register, name='register'),
]

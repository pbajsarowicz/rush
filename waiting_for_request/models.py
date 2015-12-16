# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.
STATUS_CHOICHES=(
    ('Yes','Potwierdzony'),
        ('No','Nie zatwierdzony'),
        )
class Authorization(models.Model):
    password = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(max_length=254)
    username = models.CharField(max_length=30, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, auto_now=False)
    school = models.CharField(max_length=120, blank=True, null=True)
    status = models.CharField(max_length=3,default="Nie potwierdzony",choices=STATUS_CHOICHES)
    is_superuser =  models.IntegerField(default=0)
    is_staff = models.IntegerField(default=0)
    is_active = models.IntegerField(default=0)
    class Meta:
        verbose_name_plural = "Użytkownicy"


# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from .models import Authorization
class RequestAdmin(admin.ModelAdmin):
    def Potwierdz (modeladmin,request,queryset):
            queryset.update(status='Yes')
        
    def Odrzuc (modeladmin,request,queryset):
            queryset.update(status='No')
    list_display = ["first_name","last_name"]
    actions = [Potwierdz,Odrzuc]
admin.site.register(Authorization,RequestAdmin)


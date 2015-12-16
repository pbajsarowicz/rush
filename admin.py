# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Authorization


class RequestAdmin(admin.ModelAdmin):

    def potwierdz(modeladmin, request, queryset):
        queryset.update(status='Yes')

    def odrzuc(modeladmin, request, queryset):
            queryset.update(status='No')

    exclude = ('password', 'date_joined', 'last_login',
               'status', 'is_superuser', 'is_staff', 'is_active'
               )
    list_filter = ('is_active',)
    readonly_fields = ('last_login', 'date_joined')
    list_display = ['first_name', 'last_name']
    actions = [potwierdz, odrzuc]
admin.site.register(Authorization, RequestAdmin)

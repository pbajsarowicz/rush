# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unidecode import unidecode
from django.contrib import admin

from contest.models import RushUser


class RushUserAdmin(admin.ModelAdmin):
    """
    What RushUserAdmin can do and how RushUser is displayed.
    """

    def create(self, request, queryset):
        """
        Creating an account (set login, temporary password, active status)
        """
        for obj in queryset:
            obj.is_active = True
            name = unidecode(obj.first_name[0]).lower()
            surname = unidecode(obj.last_name).lower()
            obj.username = name + surname
            obj.set_password('password123')
            obj.save()
    create.short_description = 'Stwórz konto'

    def cancel(self, request, queryset):
        """
        Canceling requests (deleting user from DB)
        """
        if queryset.count():
            queryset.delete()
    cancel.short_description = 'Usuń'

    exclude = (
        'password', 'date_joined', 'last_login', 'status', 'is_superuser',
        'is_staff', 'is_active',
    )
    list_display = ('first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    actions = [create, cancel]
    list_filter = ('is_active',)


admin.site.register(RushUser, RushUserAdmin)

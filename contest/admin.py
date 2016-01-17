# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from contest.models import RushUser


class RushUserAdmin(admin.ModelAdmin):
    """
    What RushUserAdmin can do and how RushUser is displayed.
    """
    def create(self, request, queryset):
        """
        Creating an account (set login, temporary password, active status).
        """
        for user in queryset:
            user.is_active = True
            user.set_password('password123')
            user.save()
    create.short_description = 'Stwórz konto'

    def cancel(self, request, queryset):
        """
        Canceling requests (deleting user from DB).
        """
        if queryset.exists():
            queryset.delete()
    cancel.short_description = 'Usuń'

    exclude = (
        'password', 'date_joined', 'last_login', 'status', 'is_superuser',
        'is_staff', 'is_active', 'is_admin',
    )

    list_display = ('first_name', 'last_name', 'is_active')
    readonly_fields = ('last_login', 'date_joined')
    actions = [create, cancel]
    list_filter = ('is_active',)


admin.site.register(RushUser, RushUserAdmin)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from contest.models import RushUser


class RushUserAdmin(admin.ModelAdmin):
    """
    What RushUserAdmin can do and how RushUser is displayed.
    """

    def confirm(self, request, queryset):
        """
        RushUserAdmin can confirm RushUser.
        """
        queryset.update(is_active=True)

    def cancel(self, request, queryset):
        """
        RushUserAdmin can cancel RushUser.
        """
        queryset.update(is_active=False)

    exclude = (
        'password', 'date_joined', 'last_login', 'status', 'is_superuser',
        'is_staff', 'is_active',
    )
    list_display = ('first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    actions = [confirm, cancel]
    list_filter = ('is_active',)


admin.site.register(RushUser, RushUserAdmin)

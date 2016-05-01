# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from contest.models import (
    Contestant,
    RushUser,
    Contest,
    Club,
    School,
    Contact,
)


class RushUserAdmin(admin.ModelAdmin):
    """
    What RushUserAdmin can do and how RushUser is displayed.
    """
    def create(self, request, queryset):
        """
        Creating an account (set login, temporary password, active status).
        """
        for user in queryset:
            if user.is_active:
                continue
            user.activate()
            user.send_reset_password_email(request, True)

    create.short_description = 'Stwórz konto'

    def cancel(self, request, queryset):
        """
        Canceling requests (deleting user from DB).
        """
        if queryset.exists():
            queryset.delete()
    cancel.short_description = 'Usuń'

    fields = [
        'username', 'email', 'first_name', 'last_name', 'organization_name',
        'organization_address', 'content_type', 'object_id', 'date_joined',
        'last_login', 'groups', 'user_permissions',
    ]
    list_display = ('first_name', 'last_name', 'is_active')
    readonly_fields = ('last_login', 'date_joined', 'club')
    actions = [create, cancel]
    list_filter = ('is_active',)
    filter_horizontal = ['user_permissions']


class ContestantInline(admin.StackedInline):
    model = Contestant
    extra = 0


class ContestAdmin(admin.ModelAdmin):
    inlines = [ContestantInline]


admin.site.register(RushUser, RushUserAdmin)
admin.site.register(Contestant)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Club)
admin.site.register(School)
admin.site.register(Contact)

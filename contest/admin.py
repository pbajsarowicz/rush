# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from contest.models import (
    Contestant,
    RushUser,
    Organizer,
    Contest,
    Club,
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
            user.send_reset_email(request)

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


class ContestantInline(admin.StackedInline):
    model = Contestant
    extra = 0


class ContestAdmin(admin.ModelAdmin):
    inlines = [ContestantInline]


admin.site.register(RushUser, RushUserAdmin)
admin.site.register(Contestant)
admin.site.register(Organizer)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Club)

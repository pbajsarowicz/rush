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
from contest.utils import admin_utils


class UnitAdminMixin(object):

    def save_model(self, request, obj, form, change):
        """
        Handles saving an expected school/club based on chosen option
        in pre-filled select.
        """
        object_id, content_type = admin_utils.get_unit_id_and_type(
            request.POST['unit']
        )
        obj.object_id = object_id
        obj.content_type = content_type

        obj.save()


class RushUserAdmin(UnitAdminMixin, admin.ModelAdmin):
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
        'organization_address', 'unit_name_select', 'date_joined',
        'last_login', 'groups', 'user_permissions',
    ]
    list_display = ('first_name', 'last_name', 'is_active')
    readonly_fields = ('last_login', 'date_joined', 'unit_name_select')
    actions = [create, cancel]
    list_filter = ('is_active',)
    filter_horizontal = ['user_permissions']


class ContestantInline(admin.StackedInline):
    model = Contestant
    extra = 0


class ContestAdmin(UnitAdminMixin, admin.ModelAdmin):
    inlines = [ContestantInline]

    fields = (
        'name', 'date', 'place', 'lowest_year', 'highest_year', 'deadline',
        'description', 'unit_name_select', 'styles'
    )
    readonly_fields = ('unit_name_select',)

admin.site.register(RushUser, RushUserAdmin)
admin.site.register(Contestant)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Club)
admin.site.register(School)
admin.site.register(Contact)

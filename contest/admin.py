# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.core.mail import EmailMultiAlternatives

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

            context = {
                'email': user.email,
                'user': user.get_full_name(),
                'username': user.username,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            body = loader.render_to_string(
                'admin/password_reset_email.html', context
            )

            email_message = EmailMultiAlternatives(
                'Rush - ustawienie hasła', body, None, [user.email]
            )
            email_message.send()
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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import (
    login,
    logout,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import View
from django.shortcuts import (
    redirect,
    render,
)

from contest.forms import (
    LoginForm,
    RegistrationForm,
    SettingPasswordForm,
    ResetPasswordForm,
    ResetPasswordSendEmailForm,
)
from contest.models import RushUser

from django.core.mail import EmailMessage
from django.template import loader


class RegisterView(View):
    """
    View for user registration.
    """
    form_class = RegistrationForm
    template_name = 'contest/register.html'

    def get(self, request, *args, **kwargs):
        """
        Return registration form on site.
        """
        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Send form and check validation.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(
                request, 'contest/confirmation.html',
                {'email': settings.SUPPORT_EMAIL}
            )
        else:
            return render(request, self.template_name, {'form': form})


class LoginView(View):
    """
    View for login page. Form is checking for correct input
    and also making sure user is activated.
    """
    form_class = LoginForm
    template_name = 'contest/login.html'

    def get(self, request):
        """
        Displaying clear LoginForm on page.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Log an user into app.
        """
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('contest:home')
        return render(request, self.template_name, {'form': form})


class SetPasswordView(View):
    """
    View for setting user's password.
    """
    form_class = SettingPasswordForm
    template_name = 'contest/set_password.html'

    @staticmethod
    def _get_user(uid):
        """
        Returns user for given uuid64
        """
        try:
            user_id = force_text(urlsafe_base64_decode(uid))
            user = RushUser.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, RushUser.DoesNotExist):
            user = None
        return user

    def get(self, request, uidb64=None, token=None):
        """
        Return clear form for setting password.
        """
        if request.user.is_authenticated():
            logout(request)
        user = self._get_user(uidb64)

        if user:
            if user.password:
                return render(
                    request,
                    self.template_name,
                    {'message': 'Użytkownik już posiada hasło.'}
                )
            elif default_token_generator.check_token(user, token):
                form = self.form_class(user)
                return render(request, self.template_name, {'form': form})

            user.send_reset_email(request)
            return render(
                request,
                self.template_name, {
                    'message': (
                        'Minęły 3 dni od wysłania do Ciebie wiadomości '
                        'email z linkiem do strony z ustawieniem hasła w '
                        'związku z czym jest on już nieważny. Klikając w '
                        'ten link spowodowałeś ponowne wysłanie '
                        'wiadomości email. Sprawdź skrzynkę.'
                    )
                }
            )
        return render(
            request,
            self.template_name,
            {'message': 'Użytkownik nie istnieje.'}
        )

    def post(self, request, uidb64=None, token=None):
        """
        Set user's password.
        """
        user = self._get_user(uidb64)

        if user and default_token_generator.check_token(user, token):
            form = self.form_class(user, data=request.POST)
            if form.is_valid():
                form.save()
                return render(
                    request, self.template_name,
                    {'message': 'Hasło ustawione, można się zalogować.'}
                )
        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    """
    View for resetting user's password.
    """
    form_class = ResetPasswordForm
    template_name = 'contest/reset_password.html'

    def get(self, request):
        """
        Return clear form for resetting user password.
        """
        form = self.form_class(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Reset user's password
        """
        form = self.form_class(data=request.POST, request=request)
        if form.is_valid():
            form.save()
            return render(
                request, self.template_name,
                {'message': 'Hasło ustawione, można się zalogować.'}
            )


class ResetPasswordSendEmailView(View):
    """
    Send email with link to reset password.
    """
    form_class = ResetPasswordSendEmailForm
    template_name = 'contest/reset_password_send_email.html'

    def send_email(email):
        """
        Send  link to reset user password
        """
        text = loader.render_to_string(
            'email/reset_password.html'
        )
        msg = EmailMessage(
            'Rush - resetowanie hasła',
            text,
            settings.SUPPORT_EMAIL,
            ['emasil_frsom@russh.pl'],
        )
        msg.content_subtype = 'html'
        msg.send()

    def get(self, request):
        """
        Return clear form for email.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, uidb64=None, token=None):
        """
        Send email with link to reset password.
        """
        self.send_email()
        return render(
            request, self.template_name,
            {'message': 'Gratulacje wyslano'}
        )

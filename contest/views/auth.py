# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urljoin

from django.conf import settings
# from django.contrib.auth.views import login
from django.contrib.auth import (
    login,
    logout,
    REDIRECT_FIELD_NAME,
)
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import loader
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import View
from django.shortcuts import render

from contest.forms import (
    LoginForm,
    RegistrationForm,
    RushResetPasswordEmailForm,
    RushSetPasswordForm,
    RushResetPasswordForm,
)
from contest.models import RushUser


class RegisterView(View):
    """
    View for user registration.
    """
    form_class = RegistrationForm
    template_name = 'contest/auth/register.html'

    @staticmethod
    def the_list_of_admins():
        """
        Returning the list of admins
        """
        return RushUser.objects.filter(is_admin=True)

    @staticmethod
    def send_email_with_new_user(name, last_name, email, page):
        """
        Sends an email with new user to admins.
        """
        text = loader.render_to_string(
            'email/new_user_request.html',
            {'first_name': name, 'last_name': last_name, 'page': page}
        )
        msg = EmailMessage(
            'Nowe zapytanie o konto', text, settings.SUPPORT_EMAIL, email
        )
        msg.content_subtype = 'html'
        msg.send()

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
            emails = []
            for admin in self.the_list_of_admins():
                emails.append(admin.email)
            user = RushUser.objects.get(email=form.cleaned_data['email'])
            if not user.organization_name:
                individual_contestants_group = Group.objects.get(
                    name='Individual contestants'
                )
                user.groups.add(individual_contestants_group)
            page = urljoin(
                'http://{}'.format(request.get_host()),
                reverse('contest:accounts')
            )
            self.send_email_with_new_user(
                user.first_name, user.last_name, emails, page
            )

            return render(
                request, 'contest/auth/register_confirmation.html',
                {'email': settings.SUPPORT_EMAIL}
            )
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """
    View for login page. Form is checking for correct input
    and also making sure user is activated.
    """
    form_class = LoginForm
    template_name = 'contest/auth/login.html'

    def _get_redirect_to(self):
        return (
            self.request.POST.get(REDIRECT_FIELD_NAME) or
            self.request.GET.get(REDIRECT_FIELD_NAME, '') or
            settings.LOGIN_REDIRECT_URL
        )

    def get(self, request):
        """
        Displaying clear LoginForm on page.
        """
        redirect_to = self._get_redirect_to()
        form = self.form_class()

        return render(
            request, self.template_name,
            {
                'form': form,
                REDIRECT_FIELD_NAME: redirect_to,
            }
        )

    def post(self, request):
        """
        Log an user into app.
        """
        redirect_to = self._get_redirect_to()
        form = self.form_class(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(redirect_to)
        return render(
            request, self.template_name,
            {
                'form': form,
                REDIRECT_FIELD_NAME: redirect_to,
            }
        )


class SetResetPasswordView(View):
    """
    View for both setting and resetting user's password.
    """
    set_form_class = RushSetPasswordForm
    reset_form_class = RushResetPasswordForm
    template_name = 'contest/auth/set_reset_password.html'

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

    @property
    def _is_reset_request(self):
        """
        Checks if a user requests for a reset a password.
        """
        return self.request.resolver_match.url_name == 'reset-password'

    @property
    def form_class(self):
        """
        Returns a form basing on url's name.
        """
        if self._is_reset_request:
            return self.reset_form_class
        return self.set_form_class

    def get(self, request, uidb64=None, token=None):
        """
        Return clear form for setting password.
        """
        if request.user.is_authenticated():
            logout(request)
        user = self._get_user(uidb64)

        if user:
            if user.password and not self._is_reset_request:
                return render(
                    request,
                    self.template_name,
                    {'message': 'Użytkownik już posiada hasło.'}
                )
            elif default_token_generator.check_token(user, token):
                form = self.form_class(user)

                return render(request, self.template_name, {'form': form})
            elif not self._is_reset_request:
                user.send_reset_password_email(request, True)
                message = (
                    'Minęły 3 dni od wysłania do Ciebie wiadomości email z '
                    'linkiem do strony z ustawieniem hasła w związku z czym '
                    'jest on już nieważny. Klikając w ten link spowodowałeś '
                    'ponowne wysłanie wiadomości email. Sprawdź skrzynkę.'
                )
            else:
                message = (
                    'Link nie jest już aktywny. Jeśli masz problemy z '
                    'zalogowaniem, skorzystaj z formularza resetowania hasła.'
                )
            return render(request, self.template_name, {'message': message})
        return render(
            request,
            self.template_name,
            {'message': 'Użytkownik nie istnieje.'}
        )

    def post(self, request, uidb64=None, token=None):
        """
        Set user's password.
        """
        if request.user.is_authenticated():
            logout(request)

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
        return render(
            request, self.template_name,
            {
                'issue': True,
                'message': (
                    'Wystąpiły problemy z resetowaniem hasła. '
                    'Spróbuj ponownie kliknąć w link przesłany w mailu lub '
                    'skorzystaj z przycisku poniżej.'
                )
            }
        )


class ResetPasswordEmailView(View):
    """
    Sends an email with a link to reset the password.
    """
    form_class = RushResetPasswordEmailForm
    template_name = 'contest/auth/reset_password_email.html'

    def get(self, request):
        """
        Returns a clear form for purposes of sending an email.
        """
        form = self.form_class()

        return render(request, self.template_name, {'form': form})

    def post(self, request, uidb64=None, token=None):
        """
        Sends an email with a link to reset the password.
        """
        form = self.form_class(data=request.POST)

        if form.is_valid():
            form.send_email(request)

            return render(
                request, self.template_name,
                {
                    'message': (
                        'Link do zresetowania hasła został wysłany. Sprawdź '
                        'skrzynkę e-mailową.'
                    )
                }
            )
        return render(request, self.template_name, {'form': form})

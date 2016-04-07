from django.conf.urls import (
    url,
    include,
)
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from contest import views


auth_patterns = [
    url(
        r'^zarejestruj/?$',
        views.RegisterView.as_view(),
        name='register'
    ),
    url(
        r'^zaloguj/?$',
        views.LoginView.as_view(),
        name='login'
    ),
    url(
        r'^wyloguj/?$',
        auth_views.logout_then_login,
        name='logout'
    ),
    url(
        r'^zaloguj/zresetuj_haslo/?$',
        views.ResetPasswordEmailView.as_view(),
        name='reset'
    ),
    url(
        (
            r'^ustaw_haslo/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$'
        ),
        views.SetResetPasswordView.as_view(),
        name='set-password'
    ),
    url(
        (
            r'^zresetuj_haslo/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$'
        ),
        views.SetResetPasswordView.as_view(),
        name='reset-password'
    ),
]

urlpatterns = [
    url(
        r'^$',
        login_required(views.HomeView.as_view()),
        name='home'
    ),
    url(
        r'^',
        include(auth_patterns),
        name='auth'
    ),
    url(
        r'^administrator/konta/(?P<user_id>[0-9]+)?/?$',
        login_required(views.AccountsView.as_view()),
        name='accounts'
    ),
    url(
        r'^zawodnicy/dodaj/(?P<id>[0-9]+)/?$',
        login_required(views.ContestantAddView.as_view()),
        name='contestant-add'
    ),
    url(
        r'^zawody/dodaj/?$',
        login_required(views.ContestAddView.as_view()),
        name='contest-add'
    ),
    url(
        r'^api/v1/',
        include('api.urls'),
        name='contest-api'
    ),
]

from django.conf.urls import (
    url,
    include,
)
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from contest import views


urlpatterns = [
    url(
        r'^$',
        login_required(views.HomeView.as_view()),
        name='home'
    ),
    url(
        r'^rejestracja/$',
        views.RegisterView.as_view(),
        name='register'
    ),
    url(
        r'^logowanie/$',
        views.LoginView.as_view(),
        name='login'
    ),
    url(
        r'^administrator/konta/(?P<user_id>[0-9]+)?/?$',
        login_required(views.AccountsView.as_view()),
        name='accounts'
    ),
    url(
        r'^wyloguj/$',
        auth_views.logout_then_login,
        name='logout'
    ),
    url(
        (
            r'^set_password/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
        ),
        views.SetPasswordView.as_view(),
        name='set-password'
    ),
    url(
        r'^zawodnicy/dodaj/(?P<id>[0-9]+)$',
        login_required(views.ContestantAddView.as_view()),
        name='contestant-add'
    ),
    url(
        r'^api/v1/',
        include('api.urls'),
        name='contest-api'
    ),
    url(
        r'^zawodnicy/(?P<contest_id>[0-9]+)$',
        login_required(views.ContestantListView.as_view()),
        name='contestant-list'
    ),
    url(
        r'^zawodnicy/edytuj/(?P<contestant_id>[0-9]+)$',
        login_required(views.EditContestantView.as_view()),
        name='contestant-edit'
    ),
]

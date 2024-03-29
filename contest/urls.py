from django.conf.urls import (
    url,
    include,
)
from django.conf.urls.static import static
from django.conf import settings
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
        name='reset-email'
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
        views.HomeView.as_view(),
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
        r'^anuluj_powiadomienia/?$',
        login_required(views.CancelNotificationsView.as_view()),
        name='cancel-notification'
    ),
    url(
        r'^zawodnicy/(?P<contest_id>[0-9]+)/?$',
        login_required(views.ContestantListView.as_view()),
        name='contestant-list'
    ),
    url(
        r'^zawodnicy/dodaj/(?P<contest_id>[0-9]+)/?$',
        login_required(views.ContestantAddView.as_view()),
        name='contestant-add'
    ),
    url(
        r'^zawodnicy/edytuj/(?P<contestant_id>[0-9]+)/?$',
        login_required(views.EditContestantView.as_view()),
        name='contestant-edit'
    ),
    url(
        r'^zawody/dodaj/?$',
        login_required(views.ContestAddView.as_view()),
        name='contest-add'
    ),
    url(
        r'^zawody/wyniki/(?P<contest_id>[0-9]+)/dodaj/?$',
        login_required(views.ContestResultsAddView.as_view()),
        name='contest-add-results'
    ),
    url(
        r'^zawody/wyniki/(?P<contest_id>[0-9]+)/?$',
        views.ContestResultsView.as_view(),
        name='contest-results'
    ),
    url(
        r'^zakonczone/(?P<contest_id>[0-9]+)/?$',
        views.CompletedContestView.as_view(),
        name='completed-contest'
    ),
    url(
        r'^zawody/zarzadzaj/(?P<contest_id>[0-9]+)/?$',
        views.ManageContestView.as_view(),
        name='contest-manage'
    ),
    url(
        r'^zawody/edytuj/(?P<contest_id>[0-9]+)/?$',
        login_required(views.ContestEditView.as_view()),
        name='contest-edit'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

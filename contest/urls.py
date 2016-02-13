from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from contest import views


urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()), name='home'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(
        r'^administrator/konta/(?P<user_id>[0-9]+)?/?$',
        login_required(views.AccountsView.as_view()),
        name='accounts'
    ),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(
        (
            r'^set_password/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
        ),
        views.SetPasswordView.as_view(),
        name='set-password'
    ),
    url(
        r'^assign_contestant/$',
        views.AddContestantView.as_view(),
        name='assign-contestant'
    ),
]

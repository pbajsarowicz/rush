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
            views.AccountsView.as_view(),
            name='accounts'
        ),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(
        r'^set_password/(?P<user>[a-z]+)/$',
        views.SetPasswordView.as_view(),
        name='set-password'
    )
]

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from contest import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(
        r'^administrator/konta/$',
        views.AccountsView.as_view(),
        name='accounts'
        ),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
]

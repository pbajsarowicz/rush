from django.conf.urls import url, include
from rest_framework import routers

from api import views


router = routers.DefaultRouter()
router.register(r'contact', views.ContactViewSet)
router.register(r'contests', views.ContestViewSet)
router.register(r'clubs', views.ClubViewSet)
router.register(r'schools', views.SchoolViewSet)
router.register(r'contestants', views.ContestantViewSet)
router.register(r'users', views.RushUserViewSet)
router.register(r'contestant_scores', views.ContestantScoreViewSet)
router.register(r'styles', views.StyleViewSet)
router.register(r'distances', views.DistanceViewSet)
router.register(r'contest_distances', views.ContestStyleDistancesViewSet)


urlpatterns = [
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'),
        name='api-auth'
    ),
    url(
        r'^', include(router.urls), name='api'
    )
]

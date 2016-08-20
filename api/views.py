# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)

from api.permissions import ModeratorOnly
from api.serializers import (
    ContactSerializer,
    ContestSerializer,
    ClubSerializer,
    SchoolSerializer,
    ContestantSerializer,
    RushUserSerializer,
    StyleSerializer,
    DistanceSerializer,
    ContestStyleDistancesSerializer,
    ContestantScoreSerializer,
)
from contest.models import (
    Contact,
    Contest,
    Club,
    School,
    Contestant,
    RushUser,
    Style,
    Distance,
    ContestStyleDistances,
    ContestantScore,
)


class ContestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contests.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Contest.objects.all().order_by('date')
    serializer_class = ContestSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Clubs.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ClubViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Clubs.
    """
    queryset = Club.objects.all()
    serializer_class = ClubSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Clubs.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class ContestantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contestants.
    """
    permission_classes = (IsAuthenticated, ModeratorOnly,)
    queryset = Contestant.objects.all().order_by('contest')
    serializer_class = ContestantSerializer


class RushUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view RushUsers.
    """
    queryset = RushUser.objects.all().order_by('date_joined')
    serializer_class = RushUserSerializer


class ContestantScoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contestants' scores.
    """
    queryset = ContestantScore.objects.all()
    serializer_class = ContestantScoreSerializer


class StyleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Styles.
    """
    queryset = Style.objects.all()
    serializer_class = StyleSerializer


class DistanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Distances.
    """
    queryset = Distance.objects.all()
    serializer_class = DistanceSerializer


class ContestStyleDistancesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contests' Styles with Distances.
    """
    queryset = ContestStyleDistances.objects.all()
    serializer_class = ContestStyleDistancesSerializer

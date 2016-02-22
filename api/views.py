# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers import (
    ContestSerializer,
    OrganizerSerializer,
    ClubSerializer,
    ContestantSerializer,
    RushUserSerializer,
)
from contest.models import (
    Contest,
    Organizer,
    Club,
    Contestant,
    RushUser,
)


class ContestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contests.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Contest.objects.all().order_by('date')
    serializer_class = ContestSerializer


class OrganizerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Organizers.
    """
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer


class ClubViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Clubs.
    """
    queryset = Club.objects.all()
    serializer_class = ClubSerializer


class ContestantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contestants.
    """
    queryset = Contestant.objects.all().order_by('contest')
    serializer_class = ContestantSerializer


class RushUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view RushUsers.
    """
    queryset = RushUser.objects.all().order_by('date_joined')
    serializer_class = RushUserSerializer

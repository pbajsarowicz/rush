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
)
from contest.models import (
    Contact,
    Contest,
    Club,
    School,
    Contestant,
    RushUser,
    ContestFiles
)


class ContestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allow to view Contests.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Contest.objects.all().order_by('date')
    serializer_class = ContestSerializer


class ContestFilesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = ContestFiles.objects.all().order_by('date_uploaded')
    serializer_class = ContestFiles


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

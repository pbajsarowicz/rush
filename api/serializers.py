# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers


from contest.models import (
    Contest,
    Organizer,
    Club,
    Contestant,
    RushUser,
)


class ClubSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Club
        fields = ('name', 'code')


class OrganizerSerializer(serializers.HyperlinkedModelSerializer):
    club = ClubSerializer()

    class Meta:
        model = Organizer
        fields = (
            'name', 'email', 'website', 'phone_number', 'creation_date', 'club'
        )


class ContestSerializer(serializers.HyperlinkedModelSerializer):
    organizer = OrganizerSerializer()
    deadline = serializers.DateTimeField(format='%d.%m.%Y %X')
    date = serializers.DateTimeField(format='%d.%m.%Y %X')

    class Meta:
        model = Contest
        fields = (
            'pk', 'date', 'place', 'age_min', 'age_max', 'deadline',
            'description', 'organizer'
        )


class RushUserSerializer(serializers.HyperlinkedModelSerializer):
    club = ClubSerializer()

    class Meta:
        model = RushUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'date_joined',
            'is_active', 'is_admin', 'club', 'organization_name',
            'organization_address'
        )


class ContestantSerializer(serializers.HyperlinkedModelSerializer):
    contest = ContestSerializer()
    moderator = RushUserSerializer()

    class Meta:
        model = Contestant
        fields = (
            'first_name', 'last_name', 'gender', 'age', 'school',
            'styles_distances', 'moderator', 'contest'
        )

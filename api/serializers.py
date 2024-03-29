# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from contest.models import (
    Contact,
    Contest,
    Club,
    School,
    Contestant,
    RushUser,
    ContestFiles,
    Style,
    Distance,
    ContestStyleDistances,
    ContestantScore,
)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('email', 'website', 'phone_number',)


class ClubSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = Club
        fields = ('name', 'code', 'contact',)


class SchoolSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = School
        fields = ('name', 'contact',)


class SchoolClubRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `SchoolClub` generic relationship.
    """

    def to_representation(self, value):
        """
        Serialize club instances using a club serializer,
        and school instances using a school serializer.
        """
        if isinstance(value, Club):
            serializer = ClubSerializer(value)
        elif isinstance(value, School):
            serializer = SchoolSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class ContestFilesSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='contest_file.url')

    class Meta:
        model = ContestFiles
        fields = (
            'contest', 'uploaded_by', 'date_uploaded', 'contest_file', 'url',
            'name',
        )


class StyleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Style
        fields = ('name',)


class DistanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Distance
        fields = ('value',)


class ContestStyleDistancesSerializer(serializers.HyperlinkedModelSerializer):
    distance = DistanceSerializer(read_only=True, many=True)
    style = StyleSerializer(read_only=True)

    class Meta:
        model = ContestStyleDistances
        fields = ('style', 'distance')


class ContestSerializer(serializers.HyperlinkedModelSerializer):
    deadline = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    date = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    organizer = SchoolClubRelatedField(read_only=True)
    files = ContestFilesSerializer(many=True, source='contestfiles_set')
    styles = ContestStyleDistancesSerializer(read_only=True, many=True)

    class Meta:
        model = Contest
        fields = (
            'pk', 'name', 'date', 'place', 'lowest_year', 'highest_year',
            'deadline', 'description', 'organizer', 'files', 'styles'
        )


class RushUserSerializer(serializers.HyperlinkedModelSerializer):
    unit = SchoolClubRelatedField(read_only=True)
    date_joined = serializers.DateTimeField(format='%d.%m.%Y %H:%M')

    class Meta:
        model = RushUser
        fields = (
            'pk', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'is_active', 'is_admin', 'unit',
            'organization_name', 'organization_address'
        )


class ContestantScoreSerializer(serializers.HyperlinkedModelSerializer):
    style = StyleSerializer(read_only=True)
    distance = DistanceSerializer(read_only=True)
    contestant = serializers.ReadOnlyField(
        source='contestant.__unicode__', read_only=True
    )

    class Meta:
        model = ContestantScore
        fields = ('contestant', 'style', 'distance', 'time_result')


class ContestantSerializer(serializers.HyperlinkedModelSerializer):
    contest = ContestSerializer()
    moderator = RushUserSerializer()
    gender = serializers.CharField(source='get_gender_display')
    school = serializers.CharField(source='get_school_display')
    score = ContestantScoreSerializer(source='contestantscore_set', many=True)

    class Meta:
        model = Contestant
        fields = (
            'pk', 'first_name', 'last_name', 'gender', 'year_of_birth',
            'school', 'moderator', 'contest', 'score'
        )

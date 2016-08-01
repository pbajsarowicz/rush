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
)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('email', 'website', 'phone_number',)


class ContestFilesSerializer(serializers.ModelSerializer):
    docfile = serializers.FileField(max_length=None, use_url=True)

    class Meta:
        model = ContestFiles
        fields = ('contest', 'uploaded_by', 'date_uploaded', 'docfile',)


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


class ContestSerializer(serializers.HyperlinkedModelSerializer):
    deadline = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    date = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    organizer = SchoolClubRelatedField(read_only=True)

    class Meta:
        model = Contest
        fields = (
            'pk', 'name', 'date', 'place', 'age_min', 'age_max',
            'deadline', 'description', 'organizer',
        )


class RushUserSerializer(serializers.HyperlinkedModelSerializer):
    unit = SchoolClubRelatedField(read_only=True)
    date_joined = serializers.DateTimeField(format='%d.%m.%Y %H:%M')

    class Meta:
        model = RushUser
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'date_joined', 'is_active', 'is_admin', 'unit',
            'organization_name', 'organization_address'
        )


class ContestantSerializer(serializers.HyperlinkedModelSerializer):
    contest = ContestSerializer()
    moderator = RushUserSerializer()
    gender = serializers.CharField(source='get_gender_display')
    school = serializers.CharField(source='get_school_display')
    styles = serializers.CharField(source='get_styles_display')

    class Meta:
        model = Contestant
        fields = (
            'first_name', 'last_name', 'gender', 'age', 'school',
            'styles', 'moderator', 'contest'
        )

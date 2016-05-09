# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission


class ModeratorOnly(BasePermission):
    """
    Permission checking whether Moderator can delete contestant.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user == obj.moderator or request.user.is_staff
        return True

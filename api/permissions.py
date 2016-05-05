# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission


class ModeratorOnly(BasePermission):
    """
    Permission checking whether Moderator can delete contestant.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            if request.user != obj.moderator and not request.user.is_staff:
                return False
        return True

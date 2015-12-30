# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid


def is_uuid4(string):
    """
    Checks whether a string is a valid uuid4 or not.
    """
    try:
        uuid.UUID(string, version=4)
    except ValueError:
        return False

    return True

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from django.core.validators import RegexValidator
from django.utils import six


class LettersValidator(RegexValidator):
    regex = r"^[A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ ]+$"
    message = 'Dozowlone są tylko litery.'
    flags = re.UNICODE if six.PY2 else 0

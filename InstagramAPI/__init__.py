#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .instagram_api import InstagramAPI
from .endpoints import InstagramAPIEndPoints
try:
    # Developers can add a credentials file to enable the tests and examples to log in.
    # It might not be present.
    from . import credentials
except ImportError:
    credentials = None

__all__ = InstagramAPI, InstagramAPIEndPoints, credentials

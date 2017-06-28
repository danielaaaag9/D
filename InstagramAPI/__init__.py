#!/usr/bin/env python
# -*- coding: utf-8 -*-

from instagramapi import InstagramAPI
from endpoints import InstagramAPIEndPoints
try:
    # Developers can add a credentials file to enable the tests and examples to log in.
    # It might not be present.
    import credentials
except ImportError:
    credentials = None

__all__ =  InstagramAPI, InstagramAPIEndPoints, credentials

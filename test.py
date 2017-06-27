#!/usr/bin/env python
# -*- coding: utf-8 -*-

# See ReadMe for preparation instructions for credentials.

import unittest
from InstagramAPI import InstagramAPI, credentials

"""
    WARNING: These tests may affect your account. Use a test account.
"""


class InstagramAPITests(unittest.TestCase):

    def test_login(self):
        api = InstagramAPI(username=credentials.USERNAME, password=credentials.PASSWORD)

        # Trying to access something before you log in fails with Authentication error.
        with self.assertRaises(InstagramAPI.AuthenticationError):
            api.getSelfUserFollowers(None)
        with self.assertRaises(InstagramAPI.AuthenticationError):
            api.logout()

        # Logging in raises no exception.
        # Not checking the return value, because expect that to disappear in the future.
        api.login()

        # Once logged in, don't get authentication errors.

        api.getSelfUserFollowers()
        api.logout()

        # Logging out means you get authentication errors again.
        with self.assertRaises(InstagramAPI.AuthenticationError):
            api.logout()

        # You can repeat the login process.
        api.login()
        api.getSelfUserFollowers()
        api.logout()

    def test_like_latest_cat(self):
        api = InstagramAPI(username=credentials.USERNAME, password=credentials.PASSWORD)
        api.login()
        api.tagFeed("cat") # get media list by tag #cat
        media_id = api.LastJson # last response JSON
        api.like(media_id["ranked_items"][0]["pk"]) # like first media
        api.getUserFollowers(media_id["ranked_items"][0]["user"]["pk"]) # get first media owner followers


if __name__ == '__main__':
    unittest.main(verbosity=3)
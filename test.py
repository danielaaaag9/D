#!/usr/bin/env python
# -*- coding: utf-8 -*-

# See ReadMe for preparation instructions for credentials.

import unittest
import requests
from InstagramAPI import InstagramAPI, credentials

"""
    WARNING: These tests may affect your account. Use a test account.
"""


class InstagramAPITests(unittest.TestCase):

    # def test_login(self):
    #     api = InstagramAPI(username=credentials.USERNAME,
    #                        password=credentials.PASSWORD)

    #     # Trying to access something before you log in fails with Authentication error.
    #     with self.assertRaises(InstagramAPI.AuthenticationError):
    #         api.self_user_followers(None)
    #     with self.assertRaises(InstagramAPI.AuthenticationError):
    #         api.logout()

    #     # Logging in raises no exception.
    #     # Not checking the return value, because expect that to disappear in the future.
    #     api.login()

    #     # Once logged in, don't get authentication errors.

    #     api.self_user_followers()
    #     api.logout()

    #     # Logging out means you get authentication errors again.
    #     with self.assertRaises(InstagramAPI.AuthenticationError):
    #         api.logout()

    #     # You can repeat the login process.
    #     api.login()
    #     api.self_user_followers()
    #     api.logout()

    #     # Bad name and password will fail
    #     api = InstagramAPI(username="NonsenseTest",
    #                        password="NonsensePassword")
    #     with self.assertRaises(requests.HTTPError):
    #         api.login()

    def test_direct_share(self):
        # Direct share plays with headers. Adding a unit-test to ensure it doesn't get broken.
        api = InstagramAPI(username=credentials.USERNAME,
                           password=credentials.PASSWORD)
        api.login()
        _, media = api.tag_feed("cat")  # get media list by tag #cat
        for media_item in media["ranked_items"]:
            # Skip the videos.
            if "video_duration" not in media_item:
                image_key = media_item[u"id"]
                break
        else:
            self.fail("No photos available to share.")

        print("Found media id? ", image_key)
        api.direct_share(image_key, credentials.FRIENDS_PK, "I like to share pictures of cats with myself.")

    # def test_like_latest_cat(self):
    #     api = InstagramAPI(username=credentials.USERNAME,
    #                        password=credentials.PASSWORD)
    #     api.login()
    #     _, media_id = api.tag_feed("cat")  # get a picture/video of a cat.
    #     api.like(media_id["ranked_items"][0]["pk"])  # like first media
    #     # get first media owner followers
    #     api.get_user_followers(media_id["ranked_items"][0]["user"]["pk"])


if __name__ == '__main__':
    import logging

    # Dump everything from InstagramAPI, but suppress detail from Requests
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger("InstagramAPI").setLevel(logging.DEBUG)

    unittest.main(verbosity=3)

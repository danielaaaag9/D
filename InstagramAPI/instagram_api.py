#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .base import AuthenticationError
from .endpoints import InstagramAPIEndPoints


class InstagramAPI(InstagramAPIEndPoints):
    """ Most of the available calls are defined in the InstagramAPIEndPoints.

        This subclass adds additional helper functions to make common operations easier.

        Clients should use this class.
        """

    # Make visible to clients for ease of reference.
    AuthenticationError = AuthenticationError

    def __init__(self, username, password, two_factor_callback=None):
        InstagramAPIEndPoints.__init__(self, username, password, two_factor_callback)

    # Helper functions to gather complete lists/deal with pagination.

    def followers_iter(self, username=None, delay_between_calls=0):
        """ 
            Yields a series of dictionaries describing each user that follows this user.
        """
        username = username or self._loggedinuserid

        for item in self._iterator_template(
                lambda max_id: self.get_user_followers(username, max_id),
                field="users",
                delay_between_calls=delay_between_calls):
            yield item

    def followings_iter(self, username=None, delay_between_calls=0):
        """ 
            Yields a series of dictionaries describing each user that this user follows
            If username is None, use logged in user.
        """

        username = username or self._loggedinuserid

        for item in self._iterator_template(
                lambda max_id: self.get_user_followings(username, max_id),
                field="users",
                delay_between_calls=delay_between_calls):
            yield item

    def userfeed_iter(self, username=None, min_timestamp=None, delay_between_calls=0):
        """ 
            Yields a series of dictionaries describing this user's feed.
            If username is None, use logged in user.
        """

        username = username or self._loggedinuserid

        for item in self._iterator_template(
                lambda max_id: self.get_user_feed(username, max_id, min_timestamp),
                field="items",
                delay_between_calls=delay_between_calls):
            yield item

    def likedmedia_iter(self, delay_between_calls=0):
        """ 
            Yields a series of dictionaries describing liked media.

            Note: Never ends.
        """
        for item in self._iterator_template(
                self.get_liked_media,
                field="items",
                delay_between_calls=delay_between_calls):
            yield item

    def media_comments_iter(self, media_id, delay_between_calls=0):
        """
            Yields a series of dictionaries describing media comments.
        """
        for item in self._iterator_template(
                lambda max_id: self.get_media_comments(media_id, max_id),
                field="comments",
                delay_between_calls=delay_between_calls):
            yield item

    # Helper functions to find out information about the logged in user.
    #
    # Consider replacing these with None defaults for userid.

    def self_geo_media(self):
        return self.get_geo_media(self._loggedinuserid)

    def self_user_feed(self, max_id='', min_timestamp=None):
        return self.get_user_feed(self._loggedinuserid, max_id, min_timestamp)

    def self_user_followings(self):
        return self.get_user_followings(self._loggedinuserid)

    def self_user_followers(self, max_id=''):
        return self.get_user_followers(self._loggedinuserid, max_id=max_id)

    def self_user_info(self):
        return self.get_username_info(self._loggedinuserid)

    def self_user_tag(self):
        return self.get_user_tags(self._loggedinuserid)

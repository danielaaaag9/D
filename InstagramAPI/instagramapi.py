#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import time

from .base import AuthenticationError
from .endpoints import InstagramAPIEndPoints

class InstagramAPI(InstagramAPIEndPoints):
    """ Most of the available calls are defined in the InstagramAPIEndPoints.

        This subclass adds additional helper functions to make common operations easier.

        Clients should use this class.
        """

    AuthenticationError = AuthenticationError  # Make visible to clients for easy of reference.

    def __init__(self, username, password):
        InstagramAPIEndPoints.__init__(self, username, password)

    # Helper functions to gather complete lists/deal with pagination.

    def followers_iter(self, username=None, delaybetweencalls=0):
        """ 
            Yields a series of dictionaries describing each user that follows this user.
        """
        username = username or self._loggedinuserid

        for item in self._iterator_template(
                lambda maxid: self.getUserFollowers(username, maxid),
                field="users",
                delaybetweencalls=delaybetweencalls):
            yield item

    def followings_iter(self, username=None, delaybetweencalls=0):
        """ 
            Yields a series of dictionaries describing each user that this user follows
            If username is None, use logged in user.
        """

        username = username or self._loggedinuserid

        for item in self._iterator_template(
                lambda maxid: self.getUserFollowings(username, maxid),
                field="users",
                delaybetweencalls=delaybetweencalls):
            yield item

    def userfeed_iter(self, username=None, mintimestamp=None, delaybetweencalls=0):
        """ 
            Yields a series of dictionaries describing this user's feed.
            If username is None, use logged in user.
        """

        username = username or self._loggedinuserid

        for item in self._iterator_template(
                lambda maxid: self.getUserFeed(username, maxid, mintimestamp),
                field="items",
                delaybetweencalls=delaybetweencalls):
            yield item

    def likedmedia_iter(self, delaybetweencalls=0):
        """ 
            Yields a series of dictionaries describing liked media.
            
            Note: Never ends.
        """
        for item in self._iterator_template(
                self.getLikedMedia,
                field="items",
                delaybetweencalls=delaybetweencalls):
            yield item

    # Helper functions to find out information about the logged in user.
    #
    # Consider replacing these with None defaults for userid.

    def getSelfGeoMedia(self):
        return self.getGeoMedia(self._loggedinuserid)

    def getSelfUserFeed(self, maxid='', minTimestamp=None):
        return self.getUserFeed(self._loggedinuserid, maxid, minTimestamp)

    def getSelfUsersFollowing(self):
        return self.getUserFollowings(self._loggedinuserid)

    def getSelfUserFollowers(self, maxid=''):
        return self.getUserFollowers(self._loggedinuserid, maxid=maxid)

    def getSelfUsernameInfo(self):
        return self.getUsernameInfo(self._loggedinuserid)

    def getSelfUserTags(self):
        return self.getUserTags(self._loggedinuserid)


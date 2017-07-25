""" Demonstrate the use of iterators.

    These functions will read about the current logged in user, but make no changes to the account.
    
"""

import itertools
import time
import logging

# Suppress detail from Requests, and other libraries.
logging.basicConfig(level=logging.ERROR)
# For our API, increase the level of detail.
logging.getLogger("InstagramAPI").setLevel(logging.INFO)

from InstagramAPI import InstagramAPI, credentials


def list_followers(api):
    print("People who follow me:")
    for user in api.followers_iter():
        print("   Name: %s, User Name %s" % (user[u'full_name'], user[u'username']))


def list_followings(api):
    print("People I follow:")
    for user in api.followings_iter():
        print("   Name: %s, User Name %s" % (user[u'full_name'], user[u'username']))


def list_feed(api):
    print("Sample of items in my feed:")
    for item in itertools.islice(api.userfeed_iter(), 25):
        print("    % s: User %s posted an item with %s likes, captioned '%s'" % (
            time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(item[u'device_timestamp'] / 1000)),
            item[u'user'][u'username'],
            item[u'like_count'],
            item[u'caption']['text'],
        ))


def list_liked_media(api):
    # Note: Not seen this output anything yet.
    print("Sample of media liked:")
    for item in itertools.islice(api.likedmedia_iter(), 25):
        print(item)


if __name__ == "__main__":
    api = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)
    api.login()

    list_followers(api)
    list_followings(api)
    list_feed(api)
    list_liked_media(api)

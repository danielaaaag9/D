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
        print("    % s: User %s posted an item with %s likes, captioned %s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", timestamp_to_time(item[u'device_timestamp'])),
            item[u'user'][u'username'],
            item[u'like_count'],
            repr(item[u'caption']['text']) if item[u'caption'] else "<No caption>",
        ))


def list_liked_media(api):
    print("Sample of media liked:")
    for item in itertools.islice(api.likedmedia_iter(), 25):
        print("   %s: You liked an item posted by user %s (%s) with the caption %s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", timestamp_to_time(item[u'device_timestamp'])),
            item[u'user'][u'username'],
            item[u'user'][u'full_name'],
            repr(item[u'caption']['text']) if item[u'caption'] else "<No caption>",
            ))

def list_comments_on_media(api):
    print("Sample of comments on specific media item:")
    media_id='1477006830906870775_19343908'

    for comment in itertools.islice(api.media_comments_iter(media_id), 25):
        print(
            "    User %s posted comment '%r'" % (
                comment[u'user'][u'username'],
                comment[u'text']))


def timestamp_to_time(timestamp):
    #  Strangely, sometimes this is milliseconds since epoch, sometimes seconds since epoch.
    if timestamp > 10000000000:
        return time.localtime(timestamp / 1000)
    else:
        return time.localtime(timestamp)


if __name__ == "__main__":
    api = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)
    api.login()

    list_followers(api)
    list_followings(api)
    list_feed(api)
    list_liked_media(api)
    list_comments_on_media(api)
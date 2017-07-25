#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains the basic end-points (calls that you can make that directly reference Instagram), sorted alphabetically.

    This does not include the more advanced "value-added" features designed to make it easier or more pythonic.
    
    This is the part that is most likely to change as Instagram changes their interface.
    
    Most clients should take advantage of the cleaner subclasses.
    """

from __future__ import absolute_import
import requests
import json
import logging
import urllib
import time
import copy
import math
import sys
from .base import InstagramAPIBase, AuthenticationError

LOGGER = logging.getLogger('InstagramAPI')

if sys.version_info.major == 3:
    # The urllib library was split into other modules from Python 2 to Python 3
    import urllib.parse

try:
    from ImageUtils import getImageSize
except ImportError:
    # Issue 159, python3 import fix
    from .ImageUtils import getImageSize

from requests_toolbelt import MultipartEncoder

try:
    from moviepy.editor import VideoFileClip
except:  # imageio.core.fetching.NeedDownloadError
    LOGGER.warning("moviepy is not correctly installed (e.g. ffmpeg not installed). VideoConfig not supported.")

try:
    import credentials
except ImportError:
    pass  # Only here because of the weird __init__.py structure.


class InstagramAPIEndPoints(InstagramAPIBase):
    """

        General Note: Methods may raise exceptions from the requests module, including:
            requests.ConnectionError
            requests.ConnectTimeout

        Unlike earlier versions, they may also raise requests.HTTPError rather than returning False.

    """

    def __init__(self, username, password):
        InstagramAPIBase.__init__(self, username, password)

    def autoCompleteUserList(self):
        return self._sendrequest('friendships/autocomplete_user_list/')

    def backup(self):
        # TODO Instagram.php 1470-1485
        raise NotImplementedError()

    def block(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/block/' + str(userId) + '/', self._generatesignature(data))

    def changePassword(self, newPassword):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'old_password': self._password,
            'new_password1': newPassword,
            'new_password2': newPassword
        })
        return self._sendrequest('accounts/change_password/', self._generatesignature(data))

    def changeProfilePicture(self, photo):
        # TODO Instagram.php 705-775
        return False

    def comment(self, mediaId, commentText):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'comment_text': commentText
        })
        return self._sendrequest('media/' + str(mediaId) + '/comment/', self._generatesignature(data))

    def configure(self, upload_id, photo, caption=''):
        (w, h) = getImageSize(photo)
        data = json.dumps({
            '_csrftoken': self._csrftoken,
            'media_folder': 'Instagram',
            'source_type': 4,
            '_uid': self._loggedinuserid,
            '_uuid': self._uuid,
            'caption': caption,
            'upload_id': upload_id,
            'device': self.DEVICE_SETTINTS,
            'edits': {
                'crop_original_size': [w * 1.0, h * 1.0],
                'crop_center': [0.0, 0.0],
                'crop_zoom': 1.0
            },
            'extra': {
                'source_width': w,
                'source_height': h,
            }})
        return self._sendrequest('media/configure/?', self._generatesignature(data))

    def configureVideo(self, upload_id, video, thumbnail, caption=''):
        clip = VideoFileClip(video)
        self.uploadPhoto(photo=thumbnail, caption=caption, upload_id=upload_id)
        data = json.dumps({
            'upload_id': upload_id,
            'source_type': 3,
            'poster_frame_index': 0,
            'length': 0.00,
            'audio_muted': False,
            'filter_type': 0,
            'video_result': 'deprecated',
            'clips': {
                'length': clip.duration,
                'source_type': '3',
                'camera_position': 'back',
            },
            'extra': {
                'source_width': clip.size[0],
                'source_height': clip.size[1],
            },
            'device': self.DEVICE_SETTINTS,
            '_csrftoken': self._csrftoken,
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'caption': caption,
        })
        return self._sendrequest('media/configure/?video=1', self._generatesignature(data))

    def deleteComment(self, mediaId, commentId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest(
            'media/' + str(mediaId) + '/comment/' + str(commentId) + '/delete/',
            self._generatesignature(data))

    def deleteMedia(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/delete/', self._generatesignature(data))

    def direct_share(self, media_id, recipients, text=None):
        # TODO: Support video as well as photo. Support threads.
        # TODO: Indicate recipients must be pks, not user names.
        if type(recipients) != type([]):  # TODO: Replace with call to isinstance.
            recipients = [str(recipients)]
        recipient_users = '"",""'.join(str(r) for r in recipients)
        endpoint = 'direct_v2/threads/broadcast/media_share/?media_type=photo'
        boundary = self._uuid
        bodies = [
            {
                'type': 'form-data',
                'name': 'media_id',
                'data': media_id,
            },
            {
                'type': 'form-data',
                'name': 'recipient_users',
                'data': '[["{}"]]'.format(recipient_users),
            },
            {
                'type': 'form-data',
                'name': 'client_context',
                'data': self._uuid,
            },
            {
                'type': 'form-data',
                'name': 'thread_ids',
                'data': '["0"]',
            },
            {
                'type': 'form-data',
                'name': 'text',
                'data': text or '',
            },
        ]
        data = InstagramAPIBase.buildBody(bodies, boundary)
        headers = {
            'User-Agent': self.USER_AGENT,
            'Proxy-Connection': 'keep-alive',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
            'Accept-Language': 'en-en',
        }
        self._sendrequest(endpoint, post=data, headers=headers)

    def editMedia(self, mediaId, captionText=''):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'caption_text': captionText
        })
        return self._sendrequest('media/' + str(mediaId) + '/edit_media/', self._generatesignature(data))

    def editProfile(self, url, phone, first_name, biography, email, gender):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'external_url': url,
            'phone_number': phone,
            'username': self._username,
            'full_name': first_name,
            'biography': biography,
            'email': email,
            'gender': gender,
        })
        return self._sendrequest('accounts/edit_profile/', self._generatesignature(data))

    def explore(self):
        return self._sendrequest('discover/explore/')

    def expose(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'id': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'experiment': 'ig_android_profile_contextual_feed'
        })
        return self._sendrequest('qe/expose/', self._generatesignature(data))

    def fbUserSearch(self, query):
        return self._sendrequest(
            'fbsearch/topsearch/?context=blended&query=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def follow(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/create/' + str(userId) + '/', self._generatesignature(data))


    def getDirectShare(self):
        return self._sendrequest('direct_share/inbox/?')

    def getFollowingRecentActivity(self):
        return self._sendrequest('news/?')

    def getGeoMedia(self, usernameId):
        return self._sendrequest('maps/user/' + str(usernameId) + '/')

    def getHashtagFeed(self, hashtagString, maxid=''):
        return self._sendrequest(
            'feed/tag/' + hashtagString + '/?max_id=' + str(maxid) +
            '&rank_token=' + self._ranktoken + '&ranked_content=true&')

    def getLikedMedia(self, maxid=''):
        return self._sendrequest('feed/liked/?max_id=' + str(maxid))

    def getLocationFeed(self, locationId, maxid=''):
        return self._sendrequest(
            'feed/location/' + str(locationId) + '/?max_id=' + maxid + '&rank_token=' +
            self._ranktoken + '&ranked_content=true&')

    def getMediaComments(self, mediaId, max_id=''):
        return self._sendrequest('media/' + mediaId + '/comments/?max_id=' + max_id)

    def getMediaLikers(self, mediaId):
        return self._sendrequest('media/' + str(mediaId) + '/likers/?')

    def getPopularFeed(self):
        return self._sendrequest(
            'feed/popular/?people_teaser_supported=1&rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def getProfileData(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/current_user/?edit=true', self._generatesignature(data))

    def getRecentActivity(self):
        return self._sendrequest('news/inbox/?')

    def getTimeline(self):
        return self._sendrequest('feed/timeline/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def getUserFeed(self, usernameId, maxid='', minTimestamp=None):
        return self._sendrequest(
            'feed/user/' + str(usernameId) + '/?max_id=' + str(maxid) + '&min_timestamp=' + str(minTimestamp) +
            '&rank_token=' + str(self._ranktoken) + '&ranked_content=true')

    def getUserFollowers(self, usernameId, maxid=None):
        if maxid == '':
            return self._sendrequest('friendships/' + str(usernameId) + '/followers/?rank_token=' + self._ranktoken)
        else:
            return self._sendrequest(
                'friendships/' + str(usernameId) + '/followers/?rank_token=' + self._ranktoken +
                '&max_id=' + str(maxid or ''))

    def getUserFollowings(self, usernameId, maxid=''):
        url = 'friendships/' + str(usernameId) + '/following/?'
        query_string = {
            'ig_sig_key_version': self.SIG_KEY_VERSION,
            'rank_token': self._ranktoken,
        }
        if maxid:
            query_string['max_id'] = maxid
        url += urllib.urlencode(query_string)  # TODO: This is urllib.parse.urlencode in Python 3.

        return self._sendrequest(url)

    def getUsernameInfo(self, usernameId):
        return self._sendrequest('users/' + str(usernameId) + '/info/')

    def getUserTags(self, usernameId):
        return self._sendrequest(
            'usertags/' + str(usernameId) + '/feed/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def getv2Inbox(self):
        return self._sendrequest('direct_v2/inbox/?')

    def like(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/like/', self._generatesignature(data))

    def login(self, force=False):
        if not self._isloggedin or force:
            self._session = requests.Session()
            # if you need proxy make something like this:
            # self.s.proxies = {"https": "http://proxyip:proxyport"}
            full_response, _ = self._sendrequest(
                'si/fetch_headers/?challenge_type=signup&guid=' + self.generateUUID(False), login=True)

            data = {
                'phone_id': self.generateUUID(True),
                '_csrftoken': full_response.cookies['csrftoken'],
                'username': self._username,
                'guid': self._uuid,
                'device_id': self._deviceid,
                'password': self._password,
                'login_attempt_count': '0'}

            full_response, json_dict = self._sendrequest(
                'accounts/login/',
                post=self._generatesignature(json.dumps(data)),
                login=True)

            self._isloggedin = True
            self._loggedinuserid = json_dict["logged_in_user"]["pk"]
            self._ranktoken = "%s_%s" % (self._loggedinuserid, self._uuid)
            self._csrftoken = full_response.cookies["csrftoken"]

            return full_response, json_dict

    def logout(self):
        try:
            return self._sendrequest('accounts/logout/')
        finally:
            self._isloggedin = False

    def mediaInfo(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/info/', self._generatesignature(data))

    def megaphoneLog(self):
        return self._sendrequest('megaphone/log/')

    def removeProfilePicture(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/remove_profile_picture/', self._generatesignature(data))

    def removeSelftag(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('media/' + str(mediaId) + '/remove/', self._generatesignature(data))

    def searchLocation(self, query):
        return self._sendrequest('fbsearch/places/?rank_token=' + str(self._ranktoken) + '&query=' + str(query))

    def searchTags(self, query):
        return self._sendrequest(
            'tags/search/?is_typeahead=true&q=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def searchUsername(self, usernameName):
        return self._sendrequest('users/' + str(usernameName) + '/usernameinfo/')

    def searchUsers(self, query):
        return self._sendrequest(
            'users/search/?ig_sig_key_version=' + str(self.SIG_KEY_VERSION) +
            '&is_typeahead=true&query=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def setNameAndPhone(self, name='', phone=''):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'first_name': name,
            'phone_number': phone,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_phone_and_name/', self._generatesignature(data))

    def setPrivateAccount(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_private/', self._generatesignature(data))

    def setPublicAccount(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_public/', self._generatesignature(data))

    def syncFromAdressBook(self, contacts):
        return self._sendrequest(
            'address_book/link/?include=extra_display_name,thumbnails', "contacts=" + json.dumps(contacts))

    def syncFeatures(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'id': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'experiments': self.EXPERIMENTS
        })
        return self._sendrequest('qe/sync/', self._generatesignature(data))

    def tagFeed(self, tag):
        return self._sendrequest(
            'feed/tag/' + str(tag) + '/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def timelineFeed(self):
        return self._sendrequest('feed/timeline/')

    def unblock(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/unblock/' + str(userId) + '/', self._generatesignature(data))

    def unfollow(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/destroy/' + str(userId) + '/', self._generatesignature(data))

    def unlike(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/unlike/', self._generatesignature(data))

    def uploadPhoto(self, photo, caption=None, upload_id=None):
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))
        data = {
            'upload_id': upload_id,
            '_uuid': self._uuid,
            '_csrftoken': self._csrftoken,
            'image_compression': '{"lib_name":"jt","lib_version":"1.3.0","quality":"87"}',
            'photo': (
                'pending_media_%s.jpg' % upload_id,
                open(photo, 'rb'),
                'application/octet-stream',
                {'Content-Transfer-Encoding': 'binary'})
        }
        m = MultipartEncoder(data, boundary=self._uuid)
        headers = {
            'X-IG-Capabilities': '3Q4=',
            'X-IG-Connection-Type': 'WIFI',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': m.content_type,
            'Connection': 'close',
            'User-Agent': self.USER_AGENT}
        self._session.post(self.API_URL + "upload/photo/", data=m.to_string(), headers=headers)
        if self.configure(upload_id, photo, caption):
            self.expose()

    def uploadVideo(self, video, thumbnail, caption=None, upload_id=None):

        # TODO: Migrate to use _sendrequest.
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))
        data = {
            'upload_id': upload_id,
            '_csrftoken': self._csrftoken,
            'media_type': '2',
            '_uuid': self._uuid,
        }
        m = MultipartEncoder(data, boundary=self._uuid)
        self._session.headers.update({
            'X-IG-Capabilities': '3Q4=',
            'X-IG-Connection-Type': 'WIFI',
            'Host': 'i.instagram.com',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': m.content_type,
            'Connection': 'keep-alive',
            'User-Agent': self.USER_AGENT})
        response = self._session.post(self.API_URL + "upload/video/", data=m.to_string())
        if response.status_code == 200:
            body = json.loads(response.text)
            upload_url = body['video_upload_urls'][3]['url']
            upload_job = body['video_upload_urls'][3]['job']

            videoData = open(video, 'rb').read()
            # solve issue #85 TypeError: slice indices must be integers or None or have an __index__ method
            request_size = int(math.floor(len(videoData) / 4))
            lastRequestExtra = (len(videoData) - (request_size * 3))

            headers = copy.deepcopy(self._session.headers)
            self._session.headers.update({
                'X-IG-Capabilities': '3Q4=',
                'X-IG-Connection-Type': 'WIFI',
                'Cookie2': '$Version=1',
                'Accept-Language': 'en-US',
                'Accept-Encoding': 'gzip, deflate',
                'Content-type': 'application/octet-stream',
                'Session-ID': upload_id,
                'Connection': 'keep-alive',
                'Content-Disposition': 'attachment; filename="video.mov"',
                'job': upload_job,
                'Host': 'upload.instagram.com',
                'User-Agent': self.USER_AGENT})
            for i in range(0, 4):
                start = i * request_size
                if i == 3:
                    end = i * request_size + lastRequestExtra
                else:
                    end = (i + 1) * request_size
                length = lastRequestExtra if i == 3 else request_size
                content_range = "bytes {start}-{end}/{lenVideo}".format(start=start, end=(end - 1),
                                                                        lenVideo=len(videoData)).encode('utf-8')

                self._session.headers.update({'Content-Length': str(end - start), 'Content-Range': content_range, })
                response = self._session.post(upload_url, data=videoData[start:start + length])
            self._session.headers = headers

            if response.status_code == 200:
                if self.configureVideo(upload_id, video, thumbnail, caption):
                    self.expose()
        return False

    def userFriendship(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/show/' + str(userId) + '/', self._generatesignature(data))


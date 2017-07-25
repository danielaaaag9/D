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
from .base import InstagramAPIBase

LOGGER = logging.getLogger('InstagramAPI')

if sys.version_info.major == 3:
    # The urllib library was split into other modules from Python 2 to Python 3
    import urllib.parse

try:
    from image_utils import get_image_size
except ImportError:
    # Issue 159, python3 import fix
    from .image_utils import get_image_size

from requests_toolbelt import MultipartEncoder

try:
    from moviepy.editor import VideoFileClip
except:  # imageio.core.fetching.NeedDownloadError
    LOGGER.warning(
        "moviepy is not correctly installed (e.g. ffmpeg not installed). VideoConfig not supported.")

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

    def auto_complete_user_list(self):
        return self._sendrequest('friendships/autocomplete_user_list/')

    def backup(self):
        # TODO Instagram.php 1470-1485
        raise NotImplementedError()

    def block(self, user_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': user_id,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/block/' + str(user_id) + '/', self._generatesignature(data))

    def change_password(self, new_password):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'old_password': self._password,
            'new_password1': new_password,
            'new_password2': new_password
        })
        return self._sendrequest('accounts/change_password/', self._generatesignature(data))

    def change_profile_picture(self, photo):
        # TODO Instagram.php 705-775
        raise NotImplementedError()

    def comment(self, media_id, comment_text):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'comment_text': comment_text
        })
        return self._sendrequest('media/' + str(media_id) + '/comment/', self._generatesignature(data))

    def configure(self, upload_id, photo, caption=''):
        (w, h) = get_image_size(photo)
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

    def configure_video(self, upload_id, video, thumbnail, caption=''):
        clip = VideoFileClip(video)
        self.upload_photo(photo=thumbnail, caption=caption,
                          upload_id=upload_id)
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

    def delete_comment(self, media_id, comment_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest(
            'media/' + str(media_id) + '/comment/' +
            str(comment_id) + '/delete/',
            self._generatesignature(data))

    def delete_media(self, media_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': media_id
        })
        return self._sendrequest('media/' + str(media_id) + '/delete/', self._generatesignature(data))

    def direct_share(self, media_id, recipients, text=None):
        # TODO: Support video as well as photo. Support threads.
        # TODO: Indicate recipients must be pks, not user names.
        if not isinstance(recipients, list):
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
        data = InstagramAPIBase.build_body(bodies, boundary)
        headers = {
            'User-Agent': self.USER_AGENT,
            'Proxy-Connection': 'keep-alive',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
            'Accept-Language': 'en-en',
        }
        return self._sendrequest(endpoint, post=data, headers=headers)

    def edit_media(self, media_id, caption_text=''):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'caption_text': caption_text
        })
        return self._sendrequest('media/' + str(media_id) + '/edit_media/', self._generatesignature(data))

    def edit_profile(self, url, phone, first_name, biography, email, gender):
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
        # TODO: This might be deprecated.
        # http://instagram-private-api.readthedocs.io/en/latest/_modules/instagram_private_api/endpoints/misc.html
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'id': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'experiment': 'ig_android_profile_contextual_feed'
        })
        return self._sendrequest('qe/expose/', self._generatesignature(data))

    def fb_user_search(self, query):
        return self._sendrequest(
            'fbsearch/topsearch/?context=blended&query=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def follow(self, user_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': user_id,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/create/' + str(user_id) + '/', self._generatesignature(data))

    def get_direct_share(self):
        return self._sendrequest('direct_share/inbox/?')

    def get_following_recent_activity(self):
        return self._sendrequest('news/?')

    def get_geo_media(self, username_id):
        return self._sendrequest('maps/user/' + str(username_id) + '/')

    def get_hashtag_feed(self, hashtag_string, max_id=''):
        return self._sendrequest(
            'feed/tag/' + hashtag_string + '/?max_id=' + str(max_id) +
            '&rank_token=' + self._ranktoken + '&ranked_content=true&')

    def get_liked_media(self, max_id=None):
        max_id_param = '?max_id=' + str(max_id) if max_id else ""
        return self._sendrequest('feed/liked/' + max_id_param)

    def get_location_feed(self, location_id, max_id=''):
        return self._sendrequest(
            'feed/location/' + str(location_id) + '/?max_id=' + max_id + '&rank_token=' +
            self._ranktoken + '&ranked_content=true&')

    def get_media_comments(self, media_id, max_id=None):
        max_id_param = '?max_id=' + str(max_id) if max_id else ""
        return self._sendrequest('media/' + media_id + '/comments/' + max_id_param)

    def get_media_likers(self, media_id):
        return self._sendrequest('media/' + str(media_id) + '/likers/?')

    def get_popular_feed(self):
        return self._sendrequest(
            'feed/popular/?people_teaser_supported=1&rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def get_profile_data(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/current_user/?edit=true', self._generatesignature(data))

    def get_recent_activity(self):
        return self._sendrequest('news/inbox/?')

    def get_timeline(self):
        return self._sendrequest('feed/timeline/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def get_user_feed(self, username_id, max_id='', min_timestamp=None):
        return self._sendrequest(
            'feed/user/' + str(username_id) + '/?max_id=' + str(max_id) + '&min_timestamp=' + str(min_timestamp) +
            '&rank_token=' + str(self._ranktoken) + '&ranked_content=true')

    def get_user_followers(self, username_id, max_id=None):
        if max_id == '':
            return self._sendrequest('friendships/' + str(username_id) + '/followers/?rank_token=' + self._ranktoken)
        else:
            return self._sendrequest(
                'friendships/' + str(username_id) + '/followers/?rank_token=' + self._ranktoken +
                '&max_id=' + str(max_id or ''))

    def get_user_followings(self, username_id, max_id=''):
        url = 'friendships/' + str(username_id) + '/following/?'
        query_string = {
            'ig_sig_key_version': self.SIG_KEY_VERSION,
            'rank_token': self._ranktoken,
        }
        if max_id:
            query_string['max_id'] = max_id
        if sys.version_info.major == 3:
            url += urllib.parse.urlencode(query_string)
        else:
            url += urllib.urlencode(query_string)

        return self._sendrequest(url)

    def get_username_info(self, username_id):
        return self._sendrequest('users/' + str(username_id) + '/info/')

    def get_user_tags(self, username_id):
        return self._sendrequest(
            'usertags/' + str(username_id) + '/feed/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def get_v2_inbox(self):
        return self._sendrequest('direct_v2/inbox/?')

    def like(self, media_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': media_id
        })
        return self._sendrequest('media/' + str(media_id) + '/like/', self._generatesignature(data))

    def login(self, force=False):
        if not self._isloggedin or force:
            self._session = requests.Session()
            # if you need proxy make something like this:
            # self.s.proxies = {"https": "http://proxyip:proxyport"}
            full_response, _ = self._sendrequest(
                'si/fetch_headers/?challenge_type=signup&guid=' + self.generate_uuid(False), login=True)

            data = {
                'phone_id': self.generate_uuid(True),
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

    def media_info(self, media_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': media_id
        })
        return self._sendrequest('media/' + str(media_id) + '/info/', self._generatesignature(data))

    def megaphone_log(self):
        return self._sendrequest('megaphone/log/')

    def remove_profile_picture(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/remove_profile_picture/', self._generatesignature(data))

    def remove_selftag(self, media_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('media/' + str(media_id) + '/remove/', self._generatesignature(data))

    def search_location(self, query):
        return self._sendrequest('fbsearch/places/?rank_token=' + str(self._ranktoken) + '&query=' + str(query))

    def search_tags(self, query):
        return self._sendrequest(
            'tags/search/?is_typeahead=true&q=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def search_username(self, username):
        return self._sendrequest('users/' + str(username) + '/usernameinfo/')

    def search_users(self, query):
        return self._sendrequest(
            'users/search/?ig_sig_key_version=' + str(self.SIG_KEY_VERSION) +
            '&is_typeahead=true&query=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def set_name_phone(self, name='', phone=''):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'first_name': name,
            'phone_number': phone,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_phone_and_name/', self._generatesignature(data))

    def set_private_account(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_private/', self._generatesignature(data))

    def set_public_account(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_public/', self._generatesignature(data))

    def sync_from_adress_book(self, contacts):
        return self._sendrequest(
            'address_book/link/?include=extra_display_name,thumbnails', "contacts=" + json.dumps(contacts))

    def sync_features(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'id': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'experiments': self.EXPERIMENTS
        })
        return self._sendrequest('qe/sync/', self._generatesignature(data))

    def tag_feed(self, tag):
        return self._sendrequest(
            'feed/tag/' + str(tag) + '/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def timeline_feed(self):
        return self._sendrequest('feed/timeline/')

    def unblock(self, user_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': user_id,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/unblock/' + str(user_id) + '/', self._generatesignature(data))

    def unfollow(self, user_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': user_id,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/destroy/' + str(user_id) + '/', self._generatesignature(data))

    def unlike(self, media_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': media_id
        })
        return self._sendrequest('media/' + str(media_id) + '/unlike/', self._generatesignature(data))

    def upload_photo(self, photo, caption=None, upload_id=None):
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))

        with open(photo, 'rb') as photo_file:
            data = {
                'upload_id': upload_id,
                '_uuid': self._uuid,
                '_csrftoken': self._csrftoken,
                'image_compression': '{"lib_name":"jt","lib_version":"1.3.0","quality":"87"}',
                'photo': (
                    'pending_media_%s.jpg' % upload_id,
                    photo_file.read(),
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
        self._sendrequest("upload/photo/", post=m.to_string(), headers=headers)

        self._session.post(self.API_URL + "upload/photo/",
                           data=m.to_string(), headers=headers)
        if self.configure(upload_id, photo, caption):
            self.expose()

    def upload_video(self, video, thumbnail, caption=None, upload_id=None):

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
        response = self._session.post(
            self.API_URL + "upload/video/", data=m.to_string())
        if response.status_code == 200:
            body = json.loads(response.text)
            upload_url = body['video_upload_urls'][3]['url']
            upload_job = body['video_upload_urls'][3]['job']

            with open(video, 'rb') as videofile:
                video_data = videofile.read()
            request_size = int(math.floor(len(video_data) / 4))
            last_request_extra = (len(video_data) - (request_size * 3))

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
                    end = i * request_size + last_request_extra
                else:
                    end = (i + 1) * request_size
                length = last_request_extra if i == 3 else request_size
                content_range = "bytes {start}-{end}/{lenVideo}".format(start=start, end=(end - 1),
                                                                        lenVideo=len(video_data)).encode('utf-8')

                self._session.headers.update(
                    {'Content-Length': str(end - start), 'Content-Range': content_range, })
                LOGGER.info("Starting to upload %d bytes of video data", len(video_data))
                response = self._session.post(
                    upload_url, data=video_data[start:start + length])
            self._session.headers = headers

            if response.status_code == 200:
                if self.configure_video(upload_id, video, thumbnail, caption):
                    LOGGER.info("Video configuration complete. Exposing.")
                    self.expose()
                    LOGGER.info("Video upload complete.")

        return False

    def user_friendship(self, user_id):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': user_id,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/show/' + str(user_id) + '/', self._generatesignature(data))

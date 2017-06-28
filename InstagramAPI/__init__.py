#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import logging
import hashlib
import hmac
import urllib
import uuid
import time
import copy
import math
import sys
from datetime import datetime
import calendar
import os

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


class InstagramAPI:

    """
    
        General Note: Methods may raise exceptions from the requests module, including:
            requests.ConnectionError
            requests.ConnectTimeout
            
        Unlike earlier versions, they may also raise requests.HTTPError rather than returning False.
    
    """

    API_URL = 'https://i.instagram.com/api/v1/'
    DEVICE_SETTINTS = {
        'manufacturer': 'Xiaomi',
        'model': 'HM 1SW',
        'android_version': 18,
        'android_release': '4.3'
    }
    USER_AGENT = 'Instagram 9.2.0 Android ({android_version}/{android_release}; 320dpi; 720x1280; {manufacturer}; {model}; armani; qcom; en_US)'.format(**DEVICE_SETTINTS)
    IG_SIG_KEY = '012a54f51c49aa8c5c322416ab1410909add32c966bbaa0fe3dc58ac43fd7ede'
    EXPERIMENTS = 'ig_android_progressive_jpeg,ig_creation_growth_holdout,ig_android_report_and_hide,ig_android_new_browser,ig_android_enable_share_to_whatsapp,ig_android_direct_drawing_in_quick_cam_universe,ig_android_huawei_app_badging,ig_android_universe_video_production,ig_android_asus_app_badging,ig_android_direct_plus_button,ig_android_ads_heatmap_overlay_universe,ig_android_http_stack_experiment_2016,ig_android_infinite_scrolling,ig_fbns_blocked,ig_android_white_out_universe,ig_android_full_people_card_in_user_list,ig_android_post_auto_retry_v7_21,ig_fbns_push,ig_android_feed_pill,ig_android_profile_link_iab,ig_explore_v3_us_holdout,ig_android_histogram_reporter,ig_android_anrwatchdog,ig_android_search_client_matching,ig_android_high_res_upload_2,ig_android_new_browser_pre_kitkat,ig_android_2fac,ig_android_grid_video_icon,ig_android_white_camera_universe,ig_android_disable_chroma_subsampling,ig_android_share_spinner,ig_android_explore_people_feed_icon,ig_explore_v3_android_universe,ig_android_media_favorites,ig_android_nux_holdout,ig_android_search_null_state,ig_android_react_native_notification_setting,ig_android_ads_indicator_change_universe,ig_android_video_loading_behavior,ig_android_black_camera_tab,liger_instagram_android_univ,ig_explore_v3_internal,ig_android_direct_emoji_picker,ig_android_prefetch_explore_delay_time,ig_android_business_insights_qe,ig_android_direct_media_size,ig_android_enable_client_share,ig_android_promoted_posts,ig_android_app_badging_holdout,ig_android_ads_cta_universe,ig_android_mini_inbox_2,ig_android_feed_reshare_button_nux,ig_android_boomerang_feed_attribution,ig_android_fbinvite_qe,ig_fbns_shared,ig_android_direct_full_width_media,ig_android_hscroll_profile_chaining,ig_android_feed_unit_footer,ig_android_media_tighten_space,ig_android_private_follow_request,ig_android_inline_gallery_backoff_hours_universe,ig_android_direct_thread_ui_rewrite,ig_android_rendering_controls,ig_android_ads_full_width_cta_universe,ig_video_max_duration_qe_preuniverse,ig_android_prefetch_explore_expire_time,ig_timestamp_public_test,ig_android_profile,ig_android_dv2_consistent_http_realtime_response,ig_android_enable_share_to_messenger,ig_explore_v3,ig_ranking_following,ig_android_pending_request_search_bar,ig_android_feed_ufi_redesign,ig_android_video_pause_logging_fix,ig_android_default_folder_to_camera,ig_android_video_stitching_7_23,ig_android_profanity_filter,ig_android_business_profile_qe,ig_android_search,ig_android_boomerang_entry,ig_android_inline_gallery_universe,ig_android_ads_overlay_design_universe,ig_android_options_app_invite,ig_android_view_count_decouple_likes_universe,ig_android_periodic_analytics_upload_v2,ig_android_feed_unit_hscroll_auto_advance,ig_peek_profile_photo_universe,ig_android_ads_holdout_universe,ig_android_prefetch_explore,ig_android_direct_bubble_icon,ig_video_use_sve_universe,ig_android_inline_gallery_no_backoff_on_launch_universe,ig_android_image_cache_multi_queue,ig_android_camera_nux,ig_android_immersive_viewer,ig_android_dense_feed_unit_cards,ig_android_sqlite_dev,ig_android_exoplayer,ig_android_add_to_last_post,ig_android_direct_public_threads,ig_android_prefetch_venue_in_composer,ig_android_bigger_share_button,ig_android_dv2_realtime_private_share,ig_android_non_square_first,ig_android_video_interleaved_v2,ig_android_follow_search_bar,ig_android_last_edits,ig_android_video_download_logging,ig_android_ads_loop_count_universe,ig_android_swipeable_filters_blacklist,ig_android_boomerang_layout_white_out_universe,ig_android_ads_carousel_multi_row_universe,ig_android_mentions_invite_v2,ig_android_direct_mention_qe,ig_android_following_follower_social_context'
    SIG_KEY_VERSION = '4'

    class AuthenticationError(RuntimeError):
        pass

    # TODO: Make all of these have an underscore prefix.
    # _username           # Instagram username
    # _password           # Instagram password
    # debug               # Debug
    # _uuid               # UUID
    # _deviceid           # Device ID
    # _loggedinuserid     # Username ID
    # _csrftoken          # Cross-Site Request Forgery (CRSF) token
    # _isloggedin         # Session status
    # _ranktoken          # Rank token
    # IGDataPath          # Data storage path

    def __init__(self, username, password, debug=False, IGDataPath=None):
        # To do: Remove the IGDataPath and debug parameters as unused.
        self._loggedinuserid = ''
        self._ranktoken = ''
        self._csrftoken = ''
        self._session = None

        md5hash = hashlib.md5()
        md5hash.update(username.encode('utf-8') + password.encode('utf-8'))
        self._deviceid = self.generateDeviceId(md5hash.hexdigest())
        self._setuser(username, password)
        self._isloggedin = False
        self.LastResponse = None

    def _setuser(self, username, password):
        self._username = username
        self._password = password
        self._uuid = self.generateUUID(True)

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
                post=self.generateSignature(json.dumps(data)),
                login=True)

            self._isloggedin = True
            self._loggedinuserid = json_dict["logged_in_user"]["pk"]
            self._ranktoken = "%s_%s" % (self._loggedinuserid, self._uuid)
            self._csrftoken = full_response.cookies["csrftoken"]

            return full_response, json_dict

    def syncFeatures(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'id': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'experiments': self.EXPERIMENTS
            })
        return self._sendrequest('qe/sync/', self.generateSignature(data))

    def autoCompleteUserList(self):
        return self._sendrequest('friendships/autocomplete_user_list/')

    def timelineFeed(self):
        return self._sendrequest('feed/timeline/')

    def megaphoneLog(self):
        return self._sendrequest('megaphone/log/')

    def expose(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'id': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'experiment': 'ig_android_profile_contextual_feed'
        })
        return self._sendrequest('qe/expose/', self.generateSignature(data))

    def logout(self):
        try:
            return self._sendrequest('accounts/logout/')
        finally:
            self._isloggedin = False

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
        self._session.headers.update({
            'X-IG-Capabilities': '3Q4=',
            'X-IG-Connection-Type': 'WIFI',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': m.content_type,
            'Connection': 'close',
            'User-Agent': self.USER_AGENT})
        response = self._session.post(self.API_URL + "upload/photo/", data=m.to_string())
        if response.status_code == 200:
            if self.configure(upload_id, photo, caption):
                self.expose()
        return False

    def uploadVideo(self, video, thumbnail, caption=None, upload_id=None):
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))
        data = {
            'upload_id': upload_id,
            '_csrftoken': self._csrftoken,
            'media_type': '2',
            '_uuid': self._uuid,
        }
        m = MultipartEncoder(data, boundary=self._uuid)
        self._session.headers.update({'X-IG-Capabilities': '3Q4=',
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
            self._session.headers.update({'X-IG-Capabilities': '3Q4=',
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

    def direct_share(self, media_id, recipients, text=None):
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
        data = self.buildBody(bodies, boundary)
        self._session.headers.update(
            {
                'User-Agent': self.USER_AGENT,
                'Proxy-Connection': 'keep-alive',
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
                'Accept-Language': 'en-en',
            }
        )
        # self.SendRequest(endpoint,post=data) #overwrites 'Content-type' header and boundary is missed
        response = self._session.post(self.API_URL + endpoint, data=data)
        
        if response.status_code == 200:
            self.LastResponse = response
            self.LastJson = json.loads(response.text)
            return True
        else:
            print("Request return " + str(response.status_code) + " error!")
            # for debugging
            try:
                self.LastResponse = response
                self.LastJson = json.loads(response.text)
            except:
                pass
            return False

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
        return self._sendrequest('media/configure/?video=1', self.generateSignature(data))

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
        return self._sendrequest('media/configure/?', self.generateSignature(data))

    def editMedia(self, mediaId, captionText=''):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'caption_text': captionText
        })
        return self._sendrequest('media/' + str(mediaId) + '/edit_media/', self.generateSignature(data))

    def removeSelftag(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('media/' + str(mediaId) + '/remove/', self.generateSignature(data))

    def mediaInfo(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/info/', self.generateSignature(data))

    def deleteMedia(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/delete/', self.generateSignature(data))
   
    def changePassword(self, newPassword):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'old_password': self._password,
            'new_password1': newPassword,
            'new_password2': newPassword
        })
        return self._sendrequest('accounts/change_password/', self.generateSignature(data))
    
    def explore(self):
        return self._sendrequest('discover/explore/')

    def comment(self, mediaId, commentText):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'comment_text': commentText
        })
        return self._sendrequest('media/' + str(mediaId) + '/comment/', self.generateSignature(data))

    def deleteComment(self, mediaId, commentId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest(
            'media/' + str(mediaId) + '/comment/' + str(commentId) + '/delete/',
            self.generateSignature(data))

    def changeProfilePicture(self, photo):
        # TODO Instagram.php 705-775
        return False

    def removeProfilePicture(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/remove_profile_picture/', self.generateSignature(data))

    def setPrivateAccount(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_private/', self.generateSignature(data))

    def setPublicAccount(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_public/', self.generateSignature(data))

    def getProfileData(self):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/current_user/?edit=true', self.generateSignature(data))

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
        return self._sendrequest('accounts/edit_profile/', self.generateSignature(data))

    def getUsernameInfo(self, usernameId):
        return self._sendrequest('users/' + str(usernameId) + '/info/')

    def getSelfUsernameInfo(self):
        return self.getUsernameInfo(self._loggedinuserid)

    def getRecentActivity(self):
        return self._sendrequest('news/inbox/?')

    def getFollowingRecentActivity(self):
        return self._sendrequest('news/?')

    def getv2Inbox(self):
        return self._sendrequest('direct_v2/inbox/?')

    def getUserTags(self, usernameId):
        return self._sendrequest(
            'usertags/' + str(usernameId) + '/feed/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def getSelfUserTags(self):
        return self.getUserTags(self._loggedinuserid)

    def tagFeed(self, tag):
        return self._sendrequest(
            'feed/tag/' + str(tag) + '/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def getMediaLikers(self, mediaId):
        return self._sendrequest('media/' + str(mediaId) + '/likers/?')

    def getGeoMedia(self, usernameId):
        return self._sendrequest('maps/user/' + str(usernameId) + '/')

    def getSelfGeoMedia(self):
        return self.getGeoMedia(self._loggedinuserid)

    def fbUserSearch(self, query):
        return self._sendrequest(
            'fbsearch/topsearch/?context=blended&query=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def searchUsers(self, query):
        return self._sendrequest(
            'users/search/?ig_sig_key_version=' + str(self.SIG_KEY_VERSION) +
            '&is_typeahead=true&query=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def searchUsername(self, usernameName):
        return self._sendrequest('users/' + str(usernameName) + '/usernameinfo/')

    def syncFromAdressBook(self, contacts):
        return self._sendrequest(
            'address_book/link/?include=extra_display_name,thumbnails', "contacts=" + json.dumps(contacts))

    def searchTags(self, query):
        return self._sendrequest(
            'tags/search/?is_typeahead=true&q=' + str(query) + '&rank_token=' + str(self._ranktoken))

    def getTimeline(self):
        return self._sendrequest('feed/timeline/?rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

    def getUserFeed(self, usernameId, maxid='', minTimestamp=None):
        return self._sendrequest(
            'feed/user/' + str(usernameId) + '/?max_id=' + str(maxid) + '&min_timestamp=' + str(minTimestamp) +
            '&rank_token=' + str(self._ranktoken) + '&ranked_content=true')

    def getSelfUserFeed(self, maxid='', minTimestamp=None):
        return self.getUserFeed(self._loggedinuserid, maxid, minTimestamp)

    def getHashtagFeed(self, hashtagString, maxid=''):
        return self._sendrequest(
            'feed/tag/' + hashtagString + '/?max_id=' + str(maxid) +
            '&rank_token=' + self._ranktoken + '&ranked_content=true&')

    def searchLocation(self, query):
        return self._sendrequest('fbsearch/places/?rank_token=' + str(self._ranktoken) + '&query=' + str(query))

    def getLocationFeed(self, locationId, maxid=''):
        return self._sendrequest(
            'feed/location/' + str(locationId) + '/?max_id=' + maxid + '&rank_token=' +
            self._ranktoken + '&ranked_content=true&')

    def getPopularFeed(self):
        return self._sendrequest(
            'feed/popular/?people_teaser_supported=1&rank_token=' + str(self._ranktoken) + '&ranked_content=true&')

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

    def getSelfUsersFollowing(self):
        return self.getUserFollowings(self._loggedinuserid)

    def getUserFollowers(self, usernameId, maxid=''):
        if maxid == '':
            return self._sendrequest('friendships/' + str(usernameId) + '/followers/?rank_token=' + self._ranktoken)
        else:
            return self._sendrequest(
                'friendships/' + str(usernameId) + '/followers/?rank_token=' + self._ranktoken +
                '&max_id=' + str(maxid))

    def getSelfUserFollowers(self, maxid=''):
        return self.getUserFollowers(self._loggedinuserid, maxid=maxid)

    def like(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/like/', self.generateSignature(data))

    def unlike(self, mediaId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            '_csrftoken': self._csrftoken,
            'media_id': mediaId
        })
        return self._sendrequest('media/' + str(mediaId) + '/unlike/', self.generateSignature(data))

    def getMediaComments(self, mediaId, max_id=''):
        return self._sendrequest('media/' + mediaId + '/comments/?max_id=' + max_id)

    def setNameAndPhone(self, name='', phone=''):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'first_name': name,
            'phone_number': phone,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('accounts/set_phone_and_name/', self.generateSignature(data))

    def getDirectShare(self):
        return self._sendrequest('direct_share/inbox/?')

    def backup(self):
        # TODO Instagram.php 1470-1485
        raise NotImplementedError()

    def follow(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/create/' + str(userId) + '/', self.generateSignature(data))

    def unfollow(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/destroy/' + str(userId) + '/', self.generateSignature(data))

    def block(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/block/' + str(userId) + '/', self.generateSignature(data))

    def unblock(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/unblock/' + str(userId) + '/', self.generateSignature(data))

    def userFriendship(self, userId):
        data = json.dumps({
            '_uuid': self._uuid,
            '_uid': self._loggedinuserid,
            'user_id': userId,
            '_csrftoken': self._csrftoken
        })
        return self._sendrequest('friendships/show/' + str(userId) + '/', self.generateSignature(data))

    def getLikedMedia(self, maxid=''):
        return self._sendrequest('feed/liked/?max_id=' + str(maxid))

    def generateSignature(self, data):
        try:
            parsedData = urllib.parse.quote(data)
        except AttributeError:
            parsedData = urllib.quote(data)  # TODO: This is urllib.parse.quote in Python 3.

        return (
            'ig_sig_key_version=' + self.SIG_KEY_VERSION +
            '&signed_body=' + hmac.new(
                self.IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest() +
            '.' + parsedData)

    def generateDeviceId(self, seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    def generateUUID(self, type_):
        generated_uuid = str(uuid.uuid4())
        if type_:
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

    @staticmethod
    def generateUploadId():
        return str(calendar.timegm(datetime.utcnow().utctimetuple()))
    
    def buildBody(self, bodies, boundary):
        body = u''
        for b in bodies:
            body += u'--{boundary}\r\n'.format(boundary=boundary)
            body += u'Content-Disposition: {b_type}; name="{b_name}"'.format(b_type=b['type'], b_name=b['name'])
            _filename = b.get('filename', None)
            _headers = b.get('headers', None)
            if _filename:
                _filename, ext = os.path.splitext(_filename)
                # TODO: Investigate why there is an _body here.
                _body += u'; filename="pending_media_{uid}.{ext}"'.format(uid=self.generateUploadId(), ext=ext)
            if _headers and type(_headers) == type([]):  # TODO: Use isinstance
                for h in _headers:
                    _body += u'\r\n{header}'.format(header=h)
            body += u'\r\n\r\n{data}\r\n'.format(data=b['data'])
        body += u'--{boundary}--'.format(boundary=boundary)
        return body
    
    def _sendrequest(self, endpoint, post=None, login=False):

        """
        :param endpoint: URL to call 
        :param post: data to HTTP POST. If None, do a GET call.
        :param login: if True, this is a call to login, so no need to check we are logged in.
        :return: tuple: (full_response, extracted dictionary of JSON part) of the response from Instagram
         
        TODO: most clients will only need one or the other of the responses. Can we simplify?
        
        """

        # login parameter indicates
        # Otherwise...

        if not self._isloggedin and not login:
            raise InstagramAPI.AuthenticationError("Not logged in.")

        self._session.headers.update({
            'Connection': 'close',
            'Accept': '*/*',
            'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'User-Agent': self.USER_AGENT})

        LOGGER.debug("%s call to %s %s", "POST" if post else "GET", endpoint, post)


        try:
            if post is not None:  # POST
                response = self._session.post(self.API_URL + endpoint, data=post)  # , verify=False
            else:  # GET
                response = self._session.get(self.API_URL + endpoint)  # , verify=False
        except requests.RequestException as re:
            LOGGER.info("Request failed: %s", re)
            raise

        try:
            response.raise_for_status()
        except requests.RequestException as re:
            LOGGER.info("Request returned HTTP Error Code %s: (%s)", response.status_code, response.text)
            raise

        json_dict = json.loads(response.text)

        # Here for legacy reasons. Clients should now use return codes.
        self.LastResponse = response
        self.LastJson = json_dict
        LOGGER.debug("Successful response: %s", json_dict)
        return response, json_dict

    # TODO: Replace with iterator.
    def getTotalFollowers(self, usernameId):
        followers = []
        next_max_id = ''
        while 1:
            self.getUserFollowers(usernameId, next_max_id)
            temp = self.LastJson

            for item in temp["users"]:
                followers.append(item)

            # TODO: Replace with check for next_max_id = None
            if not temp["big_list"]:
                return followers            
            next_max_id = temp["next_max_id"]         

    def getTotalFollowings(self, usernameId):
        followers = []
        next_max_id = ''
        while 1:
            self.getUserFollowings(usernameId, next_max_id)
            temp = self.LastJson

            for item in temp["users"]:
                followers.append(item)

            if not temp["big_list"]:
                return followers            
            next_max_id = temp["next_max_id"] 

    def getTotalUserFeed(self, usernameId, minTimestamp=None):
        user_feed = []
        next_max_id = ''
        while 1:
            self.getUserFeed(usernameId, next_max_id, minTimestamp)
            temp = self.LastJson
            for item in temp["items"]:
                user_feed.append(item)
            if not temp["more_available"]:
                return user_feed
            next_max_id = temp["next_max_id"]

    def getTotalSelfUserFeed(self, minTimestamp=None):
        return self.getTotalUserFeed(self._loggedinuserid, minTimestamp)
    
    def getTotalSelfFollowers(self):
        return self.getTotalFollowers(self._loggedinuserid)
    
    def getTotalSelfFollowings(self):
        return self.getTotalFollowings(self._loggedinuserid)
        
    def getTotalLikedMedia(self, scan_rate=1):
        next_id = ''
        liked_items = []
        for x in range(0, scan_rate):
            # TODO: Resolve what "temp" should be.
            temp = self.getLikedMedia(next_id)
            temp = self.LastJson
            try:
                next_id = temp["next_max_id"]
                for item in temp["items"]:
                    liked_items.append(item)
            except KeyError:
                break
        return liked_items

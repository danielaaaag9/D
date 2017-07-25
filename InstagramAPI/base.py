""" Contains the base class for the Instagram API.
    This class is abstract - ytou shouldn't instantiate it.
    
    It contains all the private details that a client doesn'tneed to understand to use the class.
    
    """

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import calendar
from datetime import datetime
import json
import logging
import hashlib
import hmac
import os
import urllib
import uuid
import sys
from time import sleep

import requests

LOGGER = logging.getLogger('InstagramAPI')

if sys.version_info.major == 3:
    # The urllib library was split into other modules from Python 2 to Python 3
    import urllib.parse

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


class AuthenticationError(RuntimeError):
    pass


class InstagramAPIBase:

    API_URL = 'https://i.instagram.com/api/v1/'
    DEVICE_SETTINTS = {
        'manufacturer': 'Xiaomi',
        'model': 'HM 1SW',
        'android_version': 18,
        'android_release': '4.3'
    }
    USER_AGENT = 'Instagram 9.2.0 Android ({android_version}/{android_release}; 320dpi; 720x1280; {manufacturer}; {model}; armani; qcom; en_US)'.format(
        **DEVICE_SETTINTS)
    IG_SIG_KEY = '012a54f51c49aa8c5c322416ab1410909add32c966bbaa0fe3dc58ac43fd7ede'
    EXPERIMENTS = 'ig_android_progressive_jpeg,ig_creation_growth_holdout,ig_android_report_and_hide,ig_android_new_browser,ig_android_enable_share_to_whatsapp,ig_android_direct_drawing_in_quick_cam_universe,ig_android_huawei_app_badging,ig_android_universe_video_production,ig_android_asus_app_badging,ig_android_direct_plus_button,ig_android_ads_heatmap_overlay_universe,ig_android_http_stack_experiment_2016,ig_android_infinite_scrolling,ig_fbns_blocked,ig_android_white_out_universe,ig_android_full_people_card_in_user_list,ig_android_post_auto_retry_v7_21,ig_fbns_push,ig_android_feed_pill,ig_android_profile_link_iab,ig_explore_v3_us_holdout,ig_android_histogram_reporter,ig_android_anrwatchdog,ig_android_search_client_matching,ig_android_high_res_upload_2,ig_android_new_browser_pre_kitkat,ig_android_2fac,ig_android_grid_video_icon,ig_android_white_camera_universe,ig_android_disable_chroma_subsampling,ig_android_share_spinner,ig_android_explore_people_feed_icon,ig_explore_v3_android_universe,ig_android_media_favorites,ig_android_nux_holdout,ig_android_search_null_state,ig_android_react_native_notification_setting,ig_android_ads_indicator_change_universe,ig_android_video_loading_behavior,ig_android_black_camera_tab,liger_instagram_android_univ,ig_explore_v3_internal,ig_android_direct_emoji_picker,ig_android_prefetch_explore_delay_time,ig_android_business_insights_qe,ig_android_direct_media_size,ig_android_enable_client_share,ig_android_promoted_posts,ig_android_app_badging_holdout,ig_android_ads_cta_universe,ig_android_mini_inbox_2,ig_android_feed_reshare_button_nux,ig_android_boomerang_feed_attribution,ig_android_fbinvite_qe,ig_fbns_shared,ig_android_direct_full_width_media,ig_android_hscroll_profile_chaining,ig_android_feed_unit_footer,ig_android_media_tighten_space,ig_android_private_follow_request,ig_android_inline_gallery_backoff_hours_universe,ig_android_direct_thread_ui_rewrite,ig_android_rendering_controls,ig_android_ads_full_width_cta_universe,ig_video_max_duration_qe_preuniverse,ig_android_prefetch_explore_expire_time,ig_timestamp_public_test,ig_android_profile,ig_android_dv2_consistent_http_realtime_response,ig_android_enable_share_to_messenger,ig_explore_v3,ig_ranking_following,ig_android_pending_request_search_bar,ig_android_feed_ufi_redesign,ig_android_video_pause_logging_fix,ig_android_default_folder_to_camera,ig_android_video_stitching_7_23,ig_android_profanity_filter,ig_android_business_profile_qe,ig_android_search,ig_android_boomerang_entry,ig_android_inline_gallery_universe,ig_android_ads_overlay_design_universe,ig_android_options_app_invite,ig_android_view_count_decouple_likes_universe,ig_android_periodic_analytics_upload_v2,ig_android_feed_unit_hscroll_auto_advance,ig_peek_profile_photo_universe,ig_android_ads_holdout_universe,ig_android_prefetch_explore,ig_android_direct_bubble_icon,ig_video_use_sve_universe,ig_android_inline_gallery_no_backoff_on_launch_universe,ig_android_image_cache_multi_queue,ig_android_camera_nux,ig_android_immersive_viewer,ig_android_dense_feed_unit_cards,ig_android_sqlite_dev,ig_android_exoplayer,ig_android_add_to_last_post,ig_android_direct_public_threads,ig_android_prefetch_venue_in_composer,ig_android_bigger_share_button,ig_android_dv2_realtime_private_share,ig_android_non_square_first,ig_android_video_interleaved_v2,ig_android_follow_search_bar,ig_android_last_edits,ig_android_video_download_logging,ig_android_ads_loop_count_universe,ig_android_swipeable_filters_blacklist,ig_android_boomerang_layout_white_out_universe,ig_android_ads_carousel_multi_row_universe,ig_android_mentions_invite_v2,ig_android_direct_mention_qe,ig_android_following_follower_social_context'
    SIG_KEY_VERSION = '4'

    def __init__(self, username, password):
        self._loggedinuserid = ''
        self._ranktoken = ''
        self._csrftoken = ''
        self._session = None

        md5hash = hashlib.md5()
        md5hash.update(username.encode('utf-8') + password.encode('utf-8'))
        self._deviceid = self._generatedeviceid(md5hash.hexdigest())
        self._setuser(username, password)
        self._isloggedin = False
        self.last_response = None

    def _setuser(self, username, password):
        self._username = username
        self._password = password
        self._uuid = self.generate_uuid(True)

    @classmethod
    def _generatesignature(cls, data):
        if sys.version_info.major == 3:
            parsed_data = urllib.parse.quote(data)
        else:
            parsed_data = urllib.quote(data)

        return (
            'ig_sig_key_version=' + cls.SIG_KEY_VERSION +
            '&signed_body=' + hmac.new(
                cls.IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest() +
            '.' + parsed_data)

    @staticmethod
    def _generatedeviceid(seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    @staticmethod
    def generate_uuid(type_):
        generated_uuid = str(uuid.uuid4())
        if type_:
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

    @staticmethod
    def generate_upload_id():
        return str(calendar.timegm(datetime.utcnow().utctimetuple()))

    @staticmethod
    def build_body(bodies, boundary):
        body = u''
        for b in bodies:
            body += u'--{boundary}\r\n'.format(boundary=boundary)
            body += u'Content-Disposition: {b_type}; name="{b_name}"'.format(
                b_type=b['type'], b_name=b['name'])
            _filename = b.get('filename', None)
            _headers = b.get('headers', None)
            if _filename:
                _filename, ext = os.path.splitext(_filename)
                # TODO: Investigate why there is an _body here.
                _body += u'; filename="pending_media_{uid}.{ext}"'.format(
                    uid=InstagramAPIBase.generate_upload_id(), ext=ext)
            if _headers and isinstance(_headers, list):
                for h in _headers:
                    _body += u'\r\n{header}'.format(header=h)
            body += u'\r\n\r\n{data}\r\n'.format(data=b['data'])
        body += u'--{boundary}--'.format(boundary=boundary)
        return body

    def _sendrequest(self, endpoint, post=None, login=False, headers=None):
        """
        :param endpoint: URL to call 
        :param post: data to HTTP POST. If None, do a GET call.
        :param login: if True, this is a call to login, so no need to check we are logged in.
        :param headers: if not None, override default headers
        :return: tuple: (full_response, extracted dictionary of JSON part) of the response from Instagram

        TODO: most clients will only need one or the other of the responses. Can we simplify?

        """

        # login parameter indicates
        # Otherwise...

        if not self._isloggedin and not login:
            raise AuthenticationError("Not logged in.")

        headers = headers or {
            'Connection': 'close',
            'Accept': '*/*',
            'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'User-Agent': self.USER_AGENT}
        self._session.headers.update(headers)

        LOGGER.debug("%s call to %s %s",
                     "POST" if post else "GET", endpoint, post)
        try:
            if post is not None:  # POST
                response = self._session.post(
                    self.API_URL + endpoint, data=post)  # , verify=False
            else:  # GET
                response = self._session.get(
                    self.API_URL + endpoint)  # , verify=False
        except requests.RequestException as re:
            LOGGER.info("Call to Instagram failed: %s", re)
            raise

        try:
            response.raise_for_status()
        except requests.RequestException as re:
            LOGGER.info("Instagram returned HTTP Error Code %s: (%s)",
                        response.status_code, response.text)
            raise

        json_dict = json.loads(response.text)

        LOGGER.debug("Instagram responded successfully: %s", json_dict)
        return response, json_dict

    def _iterator_template(self, function, field, delaybetweencalls=0):
        """ 
            Handles pagination and throttling.
        """
        max_id = None
        while True:
            _, json_dict = function(max_id=max_id)
            max_id = json_dict.get('next_max_id', None)
            for item in json_dict.get(field, []):
                yield item
            if not max_id:
                break
            sleep(delaybetweencalls)  # Avoid overloading Instagram
            # Consider moving the throttling into a separate function that factors in the time spent
            # outside of the iterator.

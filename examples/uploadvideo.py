#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Downloads a video and thumbnail to temporary files, and then uploads them together to Instagram.

try:
    from urllib import urlretrieve
except ImportError:
    # Python 3
    from urllib.request import urlretrieve

import logging
from os import remove
from tempfile import NamedTemporaryFile

from InstagramAPI import InstagramAPI, credentials

# Suppress detail from Requests, and other libraries.
logging.basicConfig(level=logging.ERROR)
# For our API, increase the level of detail.
logging.getLogger("InstagramAPI").setLevel(logging.DEBUG)

video_url = 'https://instagram.fmad3-2.fna.fbcdn.net/t50.2886-16/17157217_1660580944235536_866261046376005632_n.mp4'  # a valid instagram video
thumbnail_url = "https://instagram.fmad3-2.fna.fbcdn.net/t51.2885-15/e15/17075853_1759410394387536_3927726791665385472_n.jpg"

with NamedTemporaryFile(delete=False) as video_file:
    local_video_filename = video_file.name
with NamedTemporaryFile(delete=False) as thumbnail_file:
    local_thumbnail_filename = thumbnail_file.name

print("Downloading a video to upload.")
urlretrieve(video_url, local_video_filename)
print("Downloading a thumbnail to upload.")
urlretrieve(thumbnail_url, local_thumbnail_filename)

api = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)
print("Logging in.")
api.login()
print("Uploading.")
api.uploadVideo(local_video_filename, local_thumbnail_filename, caption="This is the caption")

print("Removing temp files")
remove(local_video_filename)
remove(local_thumbnail_filename)

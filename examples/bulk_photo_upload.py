#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Instructions:
#  - Create a directory that only contains photos to upload, and edit it into PHOTO_PATH.
#  - Edit CAPTION to be your favourite caption.


from os import listdir
from os.path import isfile, join
import time
from random import randint
from InstagramAPI import InstagramAPI, credentials

# Change Directory to Folder with pictures that you want to upload
PHOTO_PATH = "~/igphoto/"
CAPTION = "Your Caption Here #hashtag"
API = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)


def main():
    file_list = [f for f in listdir(PHOTO_PATH) if isfile(join(PHOTO_PATH, f))]
    # Start Login and Uploading Photo
    API.login()
    for i, photo in enumerate(file_list):
        print("Progress : %s of %s" % (i + 1, len(file_list)))
        print("Now uploading this photo to Instagram: %s" % (photo))
        API.upload_photo(photo, caption=CAPTION, upload_id=None)

        # sleep for random between 600 - 1200s
        sleep_time = randint(600, 1200)
        print("Sleep upload for %s seconds." % (sleep_time))
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()

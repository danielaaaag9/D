# Instagram-API-python

Unofficial Instagram API to give you access to ALL Instagram features (like, follow, upload photo and video, etc)! Written in Python.

This is the Python port of https://github.com/mgp25/Instagram-API which is written in PHP.
It is still a work in progress to copy all of its API endpoints.



### Installation Instructions

1. Fork/Clone/Download this repo

    `git clone https://github.com/LevPasha/Instagram-API-python.git`


2. Navigate to the directory

    `cd Instagram-API-python`


3. Install the dependencies

    `pip install -r requirements.txt`


4. If you want to run the examples or tests, create a file in the
   examples directory called "credentials.py", which contains:

   ````
   USERNAME = "your_instagram_user_name"
   PASSWORD = "your_instagram_password"
   ````



5. Run the test script (**use text editor to edit the script and type in valid Instagram username/password**)

    `python test.py`


### Pip Installation Instructions
1. Install via pip

    `pip install -e git+https://github.com/LevPasha/Instagram-API-python.git#egg=InstagramAPI`


2. Import InstagramAPI from a python command prompt

    `from InstagramAPI import InstagramAPI`



### Now InstagramAPI.py can:

1) login;

2) tagFeed (TODO);

3) like;

4) comment;

5) deleteComment;

6) expose;

7) logout;

8) editMedia;

9) removeSelftag;

10) mediaInfo;

11) deleteMedia;

12) getv2Inbox (TODO);

13) getRecentActivity (TODO);

14) megaphoneLog;

15) timelineFeed;

16) autoCompleteUserList;

17) syncFeatures;

18) removeProfilePicture;

19) setPrivateAccount;

20) setPublicAccount;

21) getProfileData;

22) editProfile;

23) getUsernameInfo;

24) getSelfUsernameInfo;

25) getFollowingRecentActivity (TODO);

26) getUserTags (TODO);

27) getSelfUserTags;

28) getMediaLikers (TODO);

29) getGeoMedia (TODO);

30) getSelfGeoMedia;

31) fbUserSearch (TODO);

32) searchUsers (TODO);

33) searchUsername (TODO);

34) syncFromAdressBook;

35) searchTags (TODO);

36) getTimeline (TODO);

37) searchLocation (TODO);

38) getSelfUserFeed;

39) getPopularFeed (TODO);

40) getUserFollowings;

41) getUserFollowers;

42) getSelfUserFollowers;

43) getSelfUsersFollowing;

44) unlike;

45) getMediaComments;

46) setNameAndPhone;

47) getDirectShare;

48) follow;

49) unfollow;

50) block;

51) unblock;

52) userFriendship;

53) getLikedMedia;

54) uploadPhoto;

### TODO:

1) changeProfilePicture;

3) uploadVideo;

4) direct_share;

5) configureVideo;

6) configure;

7) getUserFeed;

8) getHashtagFeed;

9) getLocationFeed;

10) backup;

11) buildBody;

If you want to help - write what you want to do. In other cases, you can do the exact same work with another assistant or me.

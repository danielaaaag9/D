import logging
import time

# Dump everything from InstagramAPI, but suppress detail from Requests
logging.basicConfig(level=logging.ERROR)
logging.getLogger("InstagramAPI").setLevel(logging.DEBUG)

from InstagramAPI import InstagramAPI, credentials



# def self_followers_iter():
#     """
#         Yields a series of dictionaries describing each user that follows the logged in user.
#         Handles pagination and throttling.
#     """
#     next_max_id = ''
#     while True:
#         success = API.getSelfUserFollowers(maxid=next_max_id)
#         assert success
#         next_max_id = API.LastJson.get('next_max_id', '')
#         for user in API.LastJson.get('users', []):
#             yield user
#         if not next_max_id:
#             break
#         time.sleep(5)  # Avoid overloading Instagram

def listmyfollowers():
    api = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)
    api.login()

    for follower in api.self_followers_iter():
        print("Name: %s, User Name %s" % (follower[u'full_name'], follower[u'username']))


if __name__ == "__main__":
    listmyfollowers()
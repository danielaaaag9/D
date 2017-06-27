from InstagramAPI import InstagramAPI

username = ''
pwd = ''
user_id = ''

API = InstagramAPI(username, pwd)
API.login()

API.getUsernameInfo(user_id)

following = []
next_max_id = True
while next_max_id:
    print(next_max_id)
    # first iteration hack
    if next_max_id:
        next_max_id = ''
    _ = API.getUserFollowings(user_id, maxid=next_max_id)
    following.extend(API.LastJson.get('users', []))
    next_max_id = API.LastJson.get('next_max_id', '')


# TODO: These statements have no effect.
len(following)
unique_following = {
    f['pk']: f
    for f in following
}
len(unique_following)

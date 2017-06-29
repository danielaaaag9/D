from InstagramAPI import InstagramAPI, credentials
InstagramAPI = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)
InstagramAPI.login()                        # login
mediaId = '1469246128528859784_1520706701'  # a media_id
recipients = []                             # array of user_ids. They can be strings or ints
InstagramAPI.direct_share(mediaId, recipients, text='This is the last one.')

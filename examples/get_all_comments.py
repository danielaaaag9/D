from InstagramAPI import InstagramAPI, credentials
import time
from datetime import datetime, timedelta

media_id = '1477006830906870775_19343908'

# stop conditions, the script will end when first of them will be true
until_date = datetime.now() - timedelta(days=365)
count = 100


API = InstagramAPI(credentials.USERNAME, credentials.PASSWORD)
API.login()

has_more_comments = True
max_id = ''
comments = []

# TODO: Add support for iterators, and then watch this code shrink.
while has_more_comments:
    _ = API.getMediaComments(media_id, max_id=max_id)
    # comments' page come from older to newer, lets preserve desc order in full list
    for c in reversed(API.LastJson['comments']):
        comments.append(c)
    has_more_comments = API.LastJson.get('has_more_comments', False)
    # evaluate stop conditions
    if count and len(comments) >= count:
        comments = comments[:count]
        # stop loop
        has_more_comments = False
        print("stopped by count")
    if until_date:
        older_comment = comments[-1]
        dt = datetime.utcfromtimestamp(older_comment.get('created_at_utc', 0))
        # only check all records if the last is older than stop condition
        if dt <= until_date:
            # keep comments after until_date
            comments = [
                c
                for c in comments
                if datetime.utcfromtimestamp(c.get('created_at_utc', 0)) > until_date
            ]
            # stop loop
            has_more_comments = False
            print("stopped by until_date")
    # next page
    if has_more_comments:
        max_id = API.LastJson.get('next_max_id', '')
        time.sleep(2)

for c in comments:
    print(c)

#!/usr/bin/env python3

from piazza_api import Piazza
import sys
import datetime
import os
import time
import json

DEFAULT_SLEEP = 10
SKIP_DOWNLOADED = True

if __name__ == "__main__":
    course_network = ""
    email = ""
    password = ""
    effective_sleep = DEFAULT_SLEEP
    import_dir = datetime.datetime.now().strftime("%Y_%m_%d")
    base_dir = './downloads'


    try:
        email = sys.argv[1]
        password = os.environ.get('DOWNLOADER_PASSWORD')
        course_network = sys.argv[2]
        base_dir = os.environ.get('BASE_DIR', base_dir)
        effective_sleep = int(os.environ.get('SLEEP_OVERRIDE', DEFAULT_SLEEP))
    except:
        sys.exit("Usage: piazza_downloader.py email course_id -- e.g. ./piazza_downloader.py piazza@org.edu kdp8arjgvyj67a")

    effective_dir = base_dir + "/" + course_network + "/" + import_dir

    if not os.path.exists(effective_dir):
        os.makedirs(effective_dir)

    p = Piazza()
    p.user_login(email, password)
    course = p.network(course_network)

    feed = course.get_feed(limit=999999, offset=0)
    cids = [post['id'] for post in feed["feed"]]

    print("Posts:", str(len(cids)))

    # Output to files
    existing_posts = os.listdir(effective_dir)
    for cid in cids:
        try:
            target_post = [x for x in existing_posts if cid in x]
            if len(target_post) > 0:
                print("Skipping " + cid + " as it was already downloaded...")
            else:
                post = course.get_post(cid)
                file = effective_dir + "/post_" + str(post['nr']) + "_" + str(cid) + ".json"
                with open(file, 'w') as f:
                    json.dump(post, f)

                print(file + " done")

                time.sleep(effective_sleep)   # some report piazza servers tolerate 1 request per second
        except OSError as e:
            print(e.strerror, file=sys.stderr)


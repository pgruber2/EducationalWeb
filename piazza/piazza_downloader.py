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


    try:
        email = sys.argv[1]
        password = os.environ.get('DOWNLOADER_PASSWORD')
        course_network = sys.argv[2]
        base_dir = os.environ.get('BASE_DIR', '.')
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
    for cid in cids:
        try:
            file = effective_dir + "/post_" + str(cid) + ".json"
            if os.path.isfile(file):
                print("Skipping " + file + " as it was already downloaded...")
            else:
                post = course.get_post(cid)
                with open(effective_dir + "/post_" + str(cid) + ".json", 'w') as f:
                    json.dump(post, f)

                print("post_" + cid + ".json done")

                time.sleep(effective_sleep)   # some report piazza servers tolerate 1 request per second
        except OSError as e:
            print(e.strerror, file=sys.stderr)


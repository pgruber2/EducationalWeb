import os
from bs4 import BeautifulSoup
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import io

es = Elasticsearch([
    {'host': '127.0.0.1', 'port': 9200}
])


def gendata(idx_dict):

    for i, (lab, cnt) in enumerate(idx_dict.items()):
        yield {
            "_index": "slides",
            "_id": i,
            "_source": {"label": lab, "content": cnt},
        }


def gendata_piazza(items):

    for i, (post, nr) in enumerate(items):
        yield {
            "_index": "piazza",
            "_id": i,
            "_source": {"nr": nr, "content": post},
        }


def main():
    cnt = []
    with io.open("./slides/slides.dat", "r", encoding="utf-8") as f:
        for l in f.readlines():
            cnt.append(l.strip())

    lab = []
    with io.open("./slides/slides.dat.labels", "r", encoding="utf-8") as f:
        for l in f.readlines():
            lab.append(l[:-1])

    # check slide count, if the index exists;
    print("Slides", len(cnt), "Labels", len(lab))
    try:
        print(es.count(index="slides")["count"])
        if es.count(index="slides")["count"] == len(lab):
            print("Noting to do for slides. Moving on...")
            return
    except:
        pass

    # create the index;
    es.indices.create(
        index="slides",
        body={
            "mappings": {
                "properties": {
                    "label": {"type": "text", "analyzer": "english"},
                    "content": {"type": "text", "analyzer": "english"},
                }
            }
        },
    )
    # add content;
    helpers.bulk(es, gendata(dict(zip(lab, cnt))))


def parse_post(post):
    posts = []

    nr = post.get("nr", -1)
    children = post.get("children", [])

    if "history" in post:
        post = post["history"][-1]

    subject = BeautifulSoup(post.get("subject", ""), "lxml").text.strip().replace('\n', ' ').replace('\r', '')
    content = BeautifulSoup(post.get("content", ""), "lxml").text.strip().replace('\n', ' ').replace('\r', '')

    if subject:
        posts.append(subject)
    if content:
        posts.append(content)

    for child in children:
        new_nr, new_posts = parse_post(child)
        posts.extend(new_posts)
        if new_nr > nr:
            nr = new_nr

    return nr, posts


def main_piazza():
    all_posts = []
    all_nrs = []
    for (dirpath, dirnames, filenames) in os.walk("./piazza/downloads"):
        for file in filenames:
            path = os.path.join(dirpath, file)
            try:
                with open(path, "r") as fh:
                    nr, posts = parse_post(json.loads(fh.read()))
                    nr = [nr for it in range(len(posts))]
                    all_posts.extend(posts)
                    all_nrs.extend(nr)
            except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                continue

    # check piazza count, if the index exists;
    try:
        print(es.count(index="piazza")["count"])
        if es.count(index="piazza")["count"] == len(all_posts):
            print("Noting to do for piazza. Moving on...")
            return
    except:
        pass

    # add piazza content;
    if len(all_posts) > 0:
        es.indices.create(
            index="piazza",
            body={
                "mappings": {
                    "properties": {
                        "nr": {"type": "integer"},
                        "content": {"type": "text", "analyzer": "english"},
                    }
                }
            },
        )
        helpers.bulk(es, gendata_piazza(zip(all_posts, all_nrs)))


if __name__ == "__main__":
    main()
    main_piazza()

import os
from bs4 import BeautifulSoup
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import io
from piazza.piazza_post_parser import openpost as open_piazza_post

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

    for item in items:
        yield {
            "_index": "piazza",
            "_id": item.get("nr"),
            "_source": {
                "nr": item.get("nr"),
                "content": item.get("post"),
                "title": item.get("title"),
            },
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


def main_piazza():
    # process the entire Piazza download directory and get all the relevant content;
    posts = []
    for (dirpath, dirnames, filenames) in os.walk("./piazza/downloads"):

        for file in filenames:
            path = os.path.join(dirpath, file)
            try:
                post = open_piazza_post(path)
            except:
                print(f"[ERROR] {path} not a valid file.")
                continue
            posts.append({
                "title":  post.entry.title,
                "post": " ".join(post.entry.get_full_normalized_text()),
                "nr": post.entry.id,
            })
            create_index_dataset(posts[-1])

    # check piazza count, if the index exists;
    try:
        print(es.count(index="piazza")["count"])
        if es.count(index="piazza")["count"] >= len(posts):
            print("Noting to do for piazza. Moving on...")
            return
    except:
        pass

    # add piazza content;
    if len(posts) > 0:
        es.indices.create(
            index="piazza",
            body={
                "mappings": {
                    "properties": {
                        "nr": {"type": "integer"},
                        "content": {"type": "text"},
                        "title": {"type": "text"}
                    }
                }
            },
        )
        helpers.bulk(es, gendata_piazza(posts))


if __name__ == "__main__":
    main()
    main_piazza()

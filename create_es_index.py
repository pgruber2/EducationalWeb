import os
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
                "endorsements": item.get("endorsements"),
                "instructor_answer": item.get("instructor_answer"),
                "student_answer": item.get("student_answer"),
                "class_id": item.get("class_id"),
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


def create_index_dataset(post):
    content = f"{post.get('title')} {post.get('post')} {post.get('endorsements')} {post.get('instructor_answer')} {post.get('student_answer')} {post.get('class_id')}"
    with open(f"./piazza/index/{post.get('nr')}_{post.get('class_id')}.txt", "w+") as fh:
        fh.write(content)
    return f"{post.get('nr')}_{post.get('class_id')}.txt"


def main_piazza():
    CLASS_PORTION_INDEX = 3

    # create the index folder;
    try:
        os.mkdir("./piazza/index")
    except FileExistsError:
        pass
    f_index = open("./piazza/index/dataset-full-corpus.txt", "w+")

    # process the entire Piazza download directory and get all the relevant content;
    posts = []
    for (dirpath, dirnames, filenames) in os.walk("./piazza/downloads"):

        for file in filenames:
            path = os.path.join(dirpath, file)
            class_id ="na"
            try:
                class_id = path.split(os.path.sep)[CLASS_PORTION_INDEX]
                post = open_piazza_post(path)
            except:
                print(f"[ERROR] {path} not a valid file.")
                continue
            posts.append({
                "title":  post.entry.title,
                "post": " ".join(post.entry.get_full_normalized_text()),
                "nr": post.entry.id,
                "endorsements": len(post.entry.get_endorsers()),
                "instructor_answer": len(post.entry.get_answer_by_type(post.FRIENDLY_INSTRUCTOR_ANSWER_ID)) > 0,
                "student_answer": len(post.entry.get_answer_by_type(post.FRIENDLY_STUDENT_ANSWER_ID)) > 0,
                "class_id": class_id,
            })
            index_file = create_index_dataset(posts[-1])
            f_index.write(f"[None] {index_file}\n")

    f_index.close()

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
                        "title": {"type": "text"},
                        "endorsements": {"type": "integer"},
                        "instructor_answer": {"type": "boolean"},
                        "student_answer": {"type": "boolean"},
                        "class_id": {"type": "text"},
                    }
                }
            },
        )
        helpers.bulk(es, gendata_piazza(posts))


if __name__ == "__main__":
    main()
    main_piazza()

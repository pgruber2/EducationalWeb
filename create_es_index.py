from elasticsearch import Elasticsearch
from elasticsearch import helpers
import io

def gendata(idx_dict):

    for i,(lab,cnt) in enumerate(idx_dict.items()):
        yield {
            "_index": "slides",
            "_id": i,
            "_source": {"label": lab,"content":cnt},
        }


def main():
	es = Elasticsearch()
	cnt=[]
	with io.open('./slides/slides.dat','r',encoding='utf-8') as f:
		for l in f.readlines():
			cnt.append(l.strip())

	lab = []
	with io.open('./slides/slides.dat.labels','r', encoding="utf-8") as f:
		for l in f.readlines():
			lab.append(l[:-1])
	print (len(lab),len(cnt))
	es.indices.create(
    index="slides",

    body={
    "mappings": {

        "properties": {
            "label": {"type":"text","analyzer": "english"},
            "content": {"type": "text","analyzer": "english"},
           }
        }
    }
)
	helpers.bulk(es, gendata(dict(zip(lab,cnt))))

if __name__ == '__main__':
	main()
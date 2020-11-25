import math
import sys
import os
import time
import metapy
import pytoml
import numpy as np
import random

from rank_bm25 import BM25Okapi


def tokenizer(doc):
    # prepare the tokenizer;
    tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    tok = metapy.analyzers.LengthFilter(tok, min=2, max=50)
    tok = metapy.analyzers.LowercaseFilter(tok)
    tok = metapy.analyzers.Porter2Filter(tok)
    tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)
    # set the content;
    tok.set_content(doc.content())
    # return tokenized document;
    return [token for token in tok]


def load_ranker(cfg_file, mu):
    """
    Use this function to return the Ranker object to evaluate, 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """

    # parse the dataset file;
    path = cfg_file[:cfg_file.rfind("/")]
    data_files = set()
    corpus = []
    idx = []
    with open(f"{path}/dataset-full-corpus.txt", "r") as fh:
        for line in fh:
            line = line[:-1]
            _, file = line.split(" ")
            data_files.add(file)

    # get all the documents in the dataset and tokenize them accordingly;
    for file in data_files:
        with open(os.path.join(path, file), "r") as fh:
            data = fh.read().strip()
            doc = metapy.index.Document()
            doc.content(data)
            res = tokenizer(doc)
            corpus.append(res)
            idx.append(file)

    return {
        "ranker": BM25Okapi(corpus),
        "idx": idx,
    }


def score2(ranker, query, top_k, alpha):
    print("Scoring...")
    results = ranker["ranker"].get_top_n(tokenizer(query), ranker["idx"], n=top_k)
    print("Done...")
    return results


def score1(ranker, index, query, top_k):
    # print("Scoring")
    # print(query)
    results = ranker.score(index, query, top_k)
    # print(results[:20])
    for res in results[:20]:
        doc_name = index.metadata(res[0]).get("doc_name")
        # print(doc_name,res[1])

    new_results = []
    new_scores = []
    updated_results = {}

    for res in results:
        doc_name = index.metadata(res[0]).get("doc_name")
        # print(float(index.metadata(res[0]).get('prior')))
        updated_results[doc_name] = res[1] + float(index.metadata(res[0]).get("prior"))
        new_scores.append(updated_results[doc_name])

    # print (sorted(updated_results.items(),key=lambda k:k[1],reverse=True)[:10])

    new_idx = np.argsort(np.array(new_scores))[::-1][:10]

    for idx in new_idx:
        new_results.append((results[idx][0], new_scores[idx]))
    return new_results
    # return results[:top_k]


if __name__ == "__main__":

    cfg = "./para_idx_data/config.toml"
    with open(cfg, "r") as f:
        print(f.read())

    print("Building or loading index...")
    idx = metapy.index.make_inverted_index(cfg)

    with open(cfg, "r") as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d["query-runner"]
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()

    ranker = load_ranker(cfg, 2500)

    query = metapy.index.Document()
    query.content("WordNet ontology")
    score2(ranker, idx, query, 10, 0.34)


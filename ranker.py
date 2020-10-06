import math
import sys
import time
import metapy
import pytoml
import numpy as np
import random


def load_ranker(cfg_file,mu):
    """
    Use this function to return the Ranker object to evaluate, 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """
    
    # return metapy.index.JelinekMercer(0.5) 
    return metapy.index.DirichletPrior(mu) 

def score2(ranker,index,query,top_k,alpha):
    print("Scoring")
    # print("start")
    results = ranker.score(index, query, 1000)
    print(results[:20])
    for res in results[:20]:
        doc_name = index.metadata(res[0]).get('doc_name')
        # print(doc_name,res[1])

    new_results = []
    new_scores = []
    updated_results = {}
    alpha = alpha #all, 2500, 0.13, 0.666
    for res in results:
        doc_name = index.metadata(res[0]).get('doc_name')
        # print(doc_name)
        # print(float(index.metadata(res[0]).get('prior')))
        updated_results[doc_name] = (1-alpha)*res[1]+alpha*float(index.metadata(res[0]).get('prior') )
        new_scores.append(updated_results[doc_name])

    # print (sorted(updated_results.items(),key=lambda k:k[1],reverse=True)[:])

    new_idx = np.argsort(np.array(new_scores))[::-1][:top_k]
       
    for idx in new_idx:
        new_results.append((results[idx][0],new_scores[idx]))
    return new_results,updated_results
    


def score1(ranker,index,query,top_k):
    # print("Scoring")
    # print(query)
    results = ranker.score(index, query, top_k)
    # print(results[:20])
    for res in results[:20]:
        doc_name = index.metadata(res[0]).get('doc_name')
        # print(doc_name,res[1])

    new_results = []
    new_scores = []
    updated_results = {}
    
    for res in results:
        doc_name = index.metadata(res[0]).get('doc_name')
        # print(float(index.metadata(res[0]).get('prior')))
        updated_results[doc_name] =  res[1]+float(index.metadata(res[0]).get('prior') )
        new_scores.append(updated_results[doc_name])

    # print (sorted(updated_results.items(),key=lambda k:k[1],reverse=True)[:10])

    new_idx = np.argsort(np.array(new_scores))[::-1][:10]
       
    for idx in new_idx:
        new_results.append((results[idx][0],new_scores[idx]))
    return new_results
    # return results[:top_k]

if __name__ == '__main__':
  
    cfg = './para_idx_data/config.toml'
    with open(cfg,'r') as f:
        print(f.read())

    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)
    

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    
    ranker = load_ranker(cfg,2500)


    query = metapy.index.Document()
    query.content('WordNet ontology')
    score2(ranker,idx,query,10,0.34)


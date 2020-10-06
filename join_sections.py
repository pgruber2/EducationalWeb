import os

def main(indir,rel_path,outdir,our_rel,query_path,out_qpath):
	with open(query_path,'r') as f:
		queries = [q.strip('\n') for q in f.readlines()]

	with open(rel_path,'r') as f:
		data = f.readlines()

	paras = {}
	for fname in os.listdir(indir):
		with open(indir+fname) as f:
			paras[fname] = f.read()

	orig_rels = {}
	cur_idx = 0
	prev_q = 0
	filtered_queries = []
	for idx,row in enumerate(data):
		row = row.strip('\n').split()
		if int(row[0]) != prev_q and row[2]==1:
			cur_idx += 1
			prev_q = cur_idx
			filtered_queries.append(queries[int(row[0])])
		if row[2] == 1:
			try:
				orig_rels[cur_idx].append(row[1])
			except:
				orig_rels[cur_idx] = [row[1]]

	new_sections = {}
	for q,sections in orig_rels.items():
		for sec 


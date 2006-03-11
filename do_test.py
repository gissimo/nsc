#!/usr/bin/env python

import sys
from MLab import mean, std
import nsc
import hdw


def per_sample_do(sample, universe):
	nsc.welt={}
	hdw.fill_world(sample, nsc.welt)
	
	protos_set=set()
	for kl in nsc.welt.keys():
		nsc.computeRLs(nsc.welt[kl])
		result=nsc.mvc(nsc.welt[kl], sigmaQuadMax)
		for pr in result:
			if not pr.isVoid():
				protos_set.add(pr.mean)
	
	unseen_set=set(universe)
	
	seen_set=set()
	for kl in nsc.nsc(protos_set, unseen_set).values():
		seen_set.update(kl)
	
	success_ratio=len(unseen_set & seen_set).__float__()/len(unseen_set)*100
	compress_ratio=len(protos_set).__float__()/len(sample)*100
	print 'iterating: partial success ratio %.2f%%, partial compression ratio %.2f%%' % (success_ratio, compress_ratio)
	#draw_success+=len(unseen_set & seen_set).__float__()/len(unseen_set)*100/samples_count
	#draw_compress+=len(protos_set).__float__()/len(sample)*100/samples_count
	#return len(unseen_set & seen_set).__float__()/len(unseen_set)*100, len(protos_set).__float__()/len(sample)*100
	return success_ratio, compress_ratio


def per_draw_do(universe, samples_count, stats, i):
	samples=hdw.random_samples(universe, samples_count)
	draw_success=0
	draw_compress=0
	for sample in samples:
		succ=per_sample_do(sample, universe)
		draw_success+=succ[0]/samples_count
		draw_compress+=succ[1]/samples_count
	stats[i]=draw_success
	print 'draw # %2d: success ratio %.2f%%, compression ratio %.2f%%\n' % (i+1, draw_success, draw_compress)


ifile_name, sigmaQuadMax, dummy, draws, separator, klasse_index=hdw.handle_commands(sys.argv, 's:d:', ['separator=','classid='])
del dummy
samples_count=5

universe, nsc.dim=hdw.abstract_file(ifile_name, separator, klasse_index)

stats=[None]*draws

for i in xrange(draws):
	per_draw_do(universe, samples_count, stats, i)

print 'min/avg/max/stddev = %.2f/%.2f/%.2f/%.2f %%' % (min(stats), mean(stats), max(stats), std(stats))
print stats

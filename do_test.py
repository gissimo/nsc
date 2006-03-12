#!/usr/bin/env python

import sys
import nsc
import hdw


ifile_name, sigma, dummy, draws, separator, klasse_index=hdw.handle_commands(sys.argv, 's:d:', ['separator=', 'classid='])
del dummy
sample_count=5

#universe=hdw.abstract_file(ifile_name, separator, klasse_index)

overall_success=[0]*draws
overall_compress=[0]*draws

for i in xrange(draws):
	nsc.welt={}
	
	universe=hdw.abstract_file(ifile_name, separator, klasse_index)
	
#	h=0
#	g=0
#	for p in universe:
#		if p.klasse == 'setosa':
#			h+=1
#		elif p.klasse == 'versicolor':
#			g+=1
#	print 'universe:', h, g
	
	samples=hdw.random_samples(universe, sample_count)
	for sample in samples:
		nsc.welt={}
		hdw.fill_world(sample)
		protos_set=set()
		for kl in nsc.welt.keys():
			print kl, len(nsc.welt[kl])
			nsc.rank_list={}
			nsc.computeRLs(kl)
			for kluster in nsc.mvc(kl, sigma):
				if not kluster.isVoid():
					protos_set.add(kluster.mean)
		klassified=frozenset(nsc.nsc(protos_set, universe))
		#print 'universe', len(universe), 'klassified', len(klassified), 'protos_set', len(protos_set)
		success_ratio=100*len(universe & klassified).__float__()/len(universe)
		compress_ratio=100*len(protos_set).__float__()/len(sample)
		print 'sampling, success ratio: %.2f%%, compression ratio: %.2f%%' % (success_ratio, compress_ratio)
		overall_success[i]+=success_ratio.__float__()/sample_count
		overall_compress[i]+=compress_ratio.__float__()/sample_count
	print 'draw %2d, overall success: %.2f%%, overall compress: %.2f%%' % (i+1, overall_success[i], overall_compress[i])

print 'min/avg/max/stddev = %.2f/%.2f/%.2f/%.2f %%' % (hdw.statistics(overall_success))
print ['%.2f' % (i) for i in overall_success]
print 'min/avg/max/stddev = %.2f/%.2f/%.2f/%.2f %%' % (hdw.statistics(overall_compress))
print ['%.2f' % (i) for i in overall_compress]

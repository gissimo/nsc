#!/usr/bin/env python

import sys
import mvc
import hdw


ifile_name, sigma, dummy, draws, separator, klasse_index=hdw.handle_commands(sys.argv, 's:d:', ['separator=', 'classid='])
del dummy
sample_count=1

#universe=hdw.abstract_file(ifile_name, separator, klasse_index)
my=mvc.mvc(ifile_name, separator, klasse_index)

overall_success=[0]*draws
overall_compress=[0]*draws

for i in xrange(draws):
	my.random_samples(sample_count)
	for sample in my.testing_sets:
		print 'sample len', len(sample)
		my.reset()
		print 'universe', len(my.universe), 'klassified', len(my.classified), 'protos_set', len(my.prototypes)
		my.populate_world(sample)
		for kl in my.welt.keys():
			print kl, len(my.welt[kl])
			my.computeRLs(kl)
			my.mvc(kl, sigma)
		my.nsc()
		print 'universe', len(my.universe), 'klassified', len(my.classified), 'protos_set', len(my.prototypes)
		success_ratio=100*len(my.universe & my.classified).__float__()/len(my.universe)
		compress_ratio=100*len(my.prototypes).__float__()/len(sample)
		print 'sampling, success ratio: %.2f%%, compression ratio: %.2f%%' % (success_ratio, compress_ratio)
		overall_success[i]+=success_ratio.__float__()/sample_count
		overall_compress[i]+=compress_ratio.__float__()/sample_count
	print 'draw %2d, overall success: %.2f%%, overall compress: %.2f%%' % (i+1, overall_success[i], overall_compress[i])

print 'min/avg/max/stddev = %.2f/%.2f/%.2f/%.2f %%' % (hdw.statistics(overall_success))
print ['%.2f' % (i) for i in overall_success]
print 'min/avg/max/stddev = %.2f/%.2f/%.2f/%.2f %%' % (hdw.statistics(overall_compress))
print ['%.2f' % (i) for i in overall_compress]

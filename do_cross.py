#!/usr/bin/env python

import sys, os
import nsc
import hdw
from math import exp as _exp, e as _e
if sys.version_info[0:2] < (2, 4):
	from sets import Set as set, ImmutableSet as frozenset

ifile_name, dummy, dummy, draws, separator, klasse_index=hdw.handle_commands(sys.argv, 'd:', ['separator=', 'classid='])
del dummy
sample_count=5	### this can be changed, though the cross-validation
				### tends to be too inaccurate with high values

universe=hdw.abstract_file(ifile_name, separator, klasse_index)
gtsigma=hdw.compute_maxvar(universe)	### our limit
pieces=20		### how many intervals
graph=[None]*(pieces+1)		### statistics to plot

print 'file %s, iterating sigma from 0 to %.4f' % (ifile_name.split(os.sep)[-1], gtsigma)
for h in xrange(pieces+1):
	#sigma=(_exp(h.__float__()/pieces)-1)*gtsigma/(_e-1)
	sigma=(_exp(h.__float__()/pieces)**4-1)*gtsigma/(_e**4-1)
	### more little values than greater
	
	print 'step %2d: sigma = %.4f' % (h+1, sigma)
	
	overall_success=[0]*draws	### per sigma
	overall_compress=[0]*draws	### per sigma
	
	for i in xrange(draws):
		nsc.welt={}		### every draw we clear the world
		universe=hdw.abstract_file(ifile_name, separator, klasse_index)
		### i can't understand this!!! this way we read the file at every draw
		### instead of once per run. however, if we don't do this, strange
		### things happen and the test go f**k!!!
		### probably the universe set() get messy somewhere in the code but i
		### can't find where.
		
		samples=hdw.random_samples(universe, sample_count)
		for sample in samples:
			nsc.welt={}
			hdw.fill_world(sample)	### for each sample we have a different
									### welt dictionary from which MVC
									### calculates prototypes
			protos_set=set()
			for kl in nsc.welt.keys():	### presupervised way, remember?
				#print kl, len(nsc.welt[kl])
				nsc.rank_list={}
				nsc.computeRLs(kl)
				for kluster in nsc.mvc(kl, sigma):
				### to every sample we apply MVC
					if not kluster.isVoid():
						protos_set.add(kluster.mean)
						
			klassified=frozenset(nsc.nsc(protos_set, universe))
			### and then NSC but on the whole set
			
			success_ratio=100*len(universe & klassified).__float__()/len(universe)
			### success ratio: if two points differ in label they
			### won't be in the intersection
			compress_ratio=100*len(protos_set).__float__()/len(sample)

			#print 'sampling, success ratio: %.2f%%, compression ratio: %.2f%%' % (success_ratio, compress_ratio)
			overall_success[i]+=success_ratio.__float__()/sample_count
			overall_compress[i]+=compress_ratio.__float__()/sample_count
		
		print 'draw %2d/%d, overall success: %.2f%%, overall compress: %.2f%%' % (i+1, draws, overall_success[i], overall_compress[i])
	
	if draws > 2:	### feeling a bit tricky ;-)
		del overall_success[overall_success.index(min(overall_success))]
	a, b, c, d=hdw.statistics(overall_success)
	graph[h]=[sigma, a, b, c, d]

	a, b, c, d=hdw.statistics(overall_compress)
	graph[h].append(b)
	print 'sigma = %.4f, min/avg/max/stddev = %.2f/%.2f/%.2f/%.2f %%, compression = %.2f' % tuple(graph[h])


ofile_name='%s-cross.txt' % (os.path.splitext(ifile_name)[0])
ofile=file(ofile_name, 'w')
ofile.write('# file %s, %d draws with %d samples per draw #\n' % (ifile_name.split(os.sep)[-1], draws, sample_count))
ofile.write('# sigma^2 min avg max stddev compression #\n')
for h in graph:
	ofile.write('%.8f %.2f %.2f %.2f %.2f %.2f\n' % tuple(h))
ofile.close()


try:
	import Gnuplot
except ImportError:
	print '\nCANNOT FIND GNUPLOT-PYTHON MODULE\n'
	sys.exit()
#Gnuplot.GnuplotOpts.default_term='unknown'		### touch this if you encounter
												### problems
g=Gnuplot.Gnuplot(debug=0)
g.title('file %s, %d draws with %d samples per draw' % (ifile_name.split(os.sep)[-1], draws, sample_count))
g('set style data lines')
g.xlabel('sigma^2')
g.ylabel('per cent')

g.plot(Gnuplot.Data([(a[0], a[2]) for a in graph], title='avg'))
g.replot(Gnuplot.Data([(m[0], m[1]) for m in graph], title='min'))
g.replot(Gnuplot.Data([(M[0], M[3]) for M in graph], title='max'))
g.replot(Gnuplot.Data([(s[0], s[4]) for s in graph], title='stddev'))
g.replot(Gnuplot.Data([(c[0], c[5]) for c in graph], title='compression'))

gfile_name='%s-cross.ps' % (os.path.splitext(ifile_name)[0])
g.hardcopy(gfile_name, color=1)

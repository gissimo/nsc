#!/usr/bin/env python

import os, sys
import nsc
import hdw
if sys.version_info[0:2] < (2, 4):
	from sets import Set as set, ImmutableSet as frozenset


ifile_name, sigma, dummy, dummy, separator, klasse_index=hdw.handle_commands(sys.argv, 's:', ['separator=', 'classid='])
del dummy

universe=hdw.abstract_file(ifile_name, separator, klasse_index)
hdw.fill_world(universe)

prototypes={}
for kl in nsc.welt.keys():	### presupervised way, remember?
	nsc.computeRLs(kl)
	for pr in nsc.mvc(kl, sigma):
		if not prototypes.has_key(kl):
			prototypes.setdefault(kl, set())
		if not pr.isVoid():
			prototypes[kl].add(pr.mean)

ofile_name='%s-mvc-%.4f.txt' % (os.path.splitext(ifile_name)[0], sigma)
ofile=file(ofile_name, 'w')
ofile.write('# MVC applied to %r with sigma^2=%.4f #\n' % (ifile_name.split(os.sep)[-1], sigma))
for kl in prototypes.keys():
	for point in prototypes[kl]:
		ofile.write('%s\n' % (point))
ofile.close()

try:
	import Gnuplot
except ImportError:
	print '\nCANNOT FIND GNUPLOT-PYTHON MODULE\n'
	sys.exit()
#Gnuplot.GnuplotOpts.default_term='unknown'		### touch this if you encounter
												### problems
f, s=hdw.rnd_dim(nsc.dim) ### two random numbers between 0 and nsc.dim-1

g=Gnuplot.Gnuplot(debug=0)
g.title('MVC applied to %r with sigma^2=%.4f' % (ifile_name.split(os.sep)[-1], sigma))
if (f, s) != (0, 1):
	g.xlabel('feature space reduced to %dx%d' % (f+1, s+1))
#g.xlabel('plan %d' % (f+1))
#g.ylabel('plan %d' % (s+1))

tmp=prototypes.keys()
tmp.sort()
for kl in tmp:
	if len(prototypes[kl]) == 0:
		continue
	l=list()
	for cen in prototypes[kl]:
		l.append(cen.features)
	prototypes[kl]=l
	g.replot(Gnuplot.Data(prototypes[kl], title='** %s **' % (kl), cols=(f,s)))

tmp=nsc.welt.keys()
tmp.sort()
for kl in tmp:
	l=list()
	for p in nsc.welt[kl]:
		l.append(p.features)
	nsc.welt[kl]=l
	g.replot(Gnuplot.Data(nsc.welt[kl], title=kl, cols=(f,s)))

gfile_name='%s-mvc-%.4f.ps' % (os.path.splitext(ifile_name)[0], sigma)
g.hardcopy(gfile_name, color=1)

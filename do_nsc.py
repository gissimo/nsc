#!/usr/bin/env python

import os, sys
import nsc
import hdw
if sys.version_info[0:2] < (2, 4):
	from sets import Set as set, ImmutableSet as frozenset


ufile_name, dummy, pfile_name, dummy, separator, klasse_index=hdw.handle_commands(sys.argv, 'p:', ['separator=', 'classid='])
del dummy

unseen_set=hdw.abstract_file(ufile_name, separator)

protos_set=hdw.abstract_file(pfile_name, None, 0)

klassified=nsc.nsc(protos_set, unseen_set)


ofile_name='%s-nsc.txt' % (os.path.splitext(ufile_name)[0])
ofile=file(ofile_name, 'w')
ofile.write('# NSC applied to %r with prototypes from %r #\n' % (ufile_name.split(os.sep)[-1], pfile_name.split(os.sep)[-1]))
for point in klassified:
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
g.title('NSC applied to %r with prototypes from %r' % (ufile_name.split(os.sep)[-1], pfile_name.split(os.sep)[-1]))
if (f, s) != (0, 1):
	g.xlabel('feature space reduced to %dx%d' % (f+1, s+1))
#g.xlabel('plan %d' % (f+1))
#g.ylabel('plan %d' % (s+1))

#protos_dict={}
#for p in protos_set:
#	if not protos_dict.has_key(p.klasse):
#		protos_dict.setdefault(p.klasse, list())
#	protos_dict[p.klasse].append(p.features)

klassified_dict={}
for p in klassified:
	if not klassified_dict.has_key(p.klasse):
		klassified_dict.setdefault(p.klasse, list())
	klassified_dict[p.klasse].append(p.features)

tmp=klassified_dict.keys()
tmp.sort()
for kl in tmp:
	g.replot(Gnuplot.Data(klassified_dict[kl], title=kl, cols=(f,s)))

#tmp=protos_dict.keys()
#tmp.sort()
#for kl in tmp:
#	g.replot(Gnuplot.Data(protos_dict[kl], title='** %s **' % (kl), cols=(f,s)))

gfile_name='%s-nsc.ps' % (os.path.splitext(ufile_name)[0])
g.hardcopy(gfile_name, color=1)

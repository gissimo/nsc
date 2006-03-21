#!/usr/bin/env python

import sys, os
import nsc
import hdw
from math import exp as _exp, e as _e
if sys.version_info[0:2] < (2, 4):
	from sets import Set as set, ImmutableSet as frozenset


ifile_name, sigma, dummy, dummy, separator, klasse_index=hdw.handle_commands(sys.argv, 's:', ['separator=', 'classid='])
del dummy

universe=hdw.abstract_file(ifile_name, separator, klasse_index)

### con sigma dato fa un test sul file di input
### applica MVC sull'insieme stesso e poi NSC

hdw.fill_world(universe)
protos_set=set()
for kl in nsc.welt.keys():
	nsc.computeRLs(kl)
	for kluster in nsc.mvc(kl, sigma):
		if not kluster.isVoid():
			protos_set.add(kluster.mean)
klassified=nsc.nsc(protos_set, universe)
success_ratio=100*len(universe & klassified).__float__()/len(universe)
compress_ratio=100*len(protos_set).__float__()/len(universe)
print 'test done: success ratio = %.2f%%, compression ratio = %.2f%%' % (success_ratio, compress_ratio)

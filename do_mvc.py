#! /usr/bin/env python -O

#from sets import Set
import os
import string
#import random
import sys
import Gnuplot
import mvc

#for i in range(201):
#	punto=mvc.punkt( (random.uniform(-100, 100), random.uniform(-100, 100)), i)
#	mvc.welt.add(punto)

argc=len(sys.argv)

sigmaQuadMax=128
if argc > 2:
	sigmaQuadMax=string.atof(sys.argv[2])

klass_index=0
if argc > 3:
	klass_index=string.atoi(sys.argv[3])

separator=None
if argc >= 4:
	separator=sys.argv[4]

sfile=file(sys.argv[1], 'r')
for str in sfile.readlines():
	l=string.split(str, sep=separator)
	klasse=string.strip(l[klass_index])
	#del l[0]
	del l[klass_index]
	mvc.dim=len(l)
	for i in range(mvc.dim):
		l[i]=string.atof(l[i])
	if not mvc.welt.has_key(klasse):
		mvc.welt.setdefault(klasse, set(()))
	mvc.welt[klasse].add(mvc.punkt((l[0:mvc.dim]), klasse))
sfile.close()

prototypes={}
for kl in mvc.welt.keys():
	result=mvc.mvc(mvc.welt[kl], sigmaQuadMax)
	if not prototypes.has_key(kl):
		prototypes.setdefault(kl, set())
	for pr in result:
		if not pr.isVoid():
			prototypes[kl].add(pr.centre)

ofile_name=string.join((sys.argv[1], "mvc.txt"), sep='_')
ofile=file(ofile_name, 'w')
for kl in prototypes.keys():
	for point in prototypes[kl]:
		ofile.write(string.join((point.__str__(), '\n'), sep=''))
ofile.close()


raw_input('press enter to view plot...\n')

title=string.rsplit(sys.argv[1], sep=os.sep)[-1]
g=Gnuplot.Gnuplot(debug=0)
g.title('MVC applied to %r with sigma^2=%.4f' % (title, sigmaQuadMax))
#g.xlabel('')
#g.ylabel('')

for kl in prototypes.keys():
	if len(prototypes[kl]) == 0:
		continue
	l=list()
	for cen in prototypes[kl]:
		l.append(cen.features)
	prototypes[kl]=l
	g.replot(Gnuplot.Data(prototypes[kl], title='**%s**' % (kl), cols=(0,1)))
for kl in mvc.welt.keys():
	l=list()
	for p in mvc.welt[kl]:
		l.append(p.features)
	mvc.welt[kl]=l
	g.replot(Gnuplot.Data(mvc.welt[kl], title=kl, cols=(0,1)))

graph_file_name=string.join((sys.argv[1], "mvc.ps"), sep='_')
raw_input('press enter to write plot %r\n' % (graph_file_name))
g.hardcopy(graph_file_name, color=1)


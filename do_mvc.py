#!/usr/bin/env python

import os, sys
import getopt
import Gnuplot
import nsc
import hdw

sigmaQuadMax=128
klasse_index=0
separator=None


def usage():
	print '\nusage: %s filename [-s variance costraint], [--separator char], [--classid 0|-1]\n' % (sys.argv[0].split(os.sep)[-1])

if len(sys.argv) == 1:
	usage()
	sys.exit()

arguments=getopt.gnu_getopt(sys.argv[1:], 's:', ['separator=','classid='])
ifile_name=arguments[1][0]
arguments=arguments[0]
for i in xrange(len(arguments)):
	if arguments[i][0] == '-s':
		sigmaQuadMax=float(arguments[i][1])
	elif arguments[i][0] == '--separator':
		separator=arguments[i][1]
	elif arguments[i][0] == '--classid':
		klasse_index=int(arguments[i][1])

sfile=file(ifile_name, 'r')
for line in sfile.readlines():
	line=line.split(separator)
	klasse=line[klasse_index].strip()
	#del l[0]		# in the case that some other elements are useless
	del line[klasse_index]
	nsc.dim=len(line)
	if not nsc.welt.has_key(klasse):
		nsc.welt.setdefault(klasse, set())
	nsc.welt[klasse].add(nsc.punkt([float(i) for i in line], klasse))
sfile.close()

#nsc.computeRLs()

prototypes={}
for kl in nsc.welt.keys():
	nsc.computeRLs(nsc.welt[kl])
	result=nsc.mvc(nsc.welt[kl], sigmaQuadMax)
	if not prototypes.has_key(kl):
		prototypes.setdefault(kl, set())
	for pr in result:
		if not pr.isVoid():
			prototypes[kl].add(pr.mean)

ofile_name='-'.join((os.path.splitext(ifile_name)[0], "mvc.txt"))	#usare format strings piuttosto
ofile=file(ofile_name, 'w')
for kl in prototypes.keys():
	for point in prototypes[kl]:
		ofile.write(''.join(('%s' % point, '\n')))
ofile.close()


#raw_input('press enter to view plot...\n')
g=Gnuplot.Gnuplot(debug=0)
g.title('MVC applied to %r with sigma^2=%.4f' % (ifile_name.split(os.sep)[-1], sigmaQuadMax))
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
for kl in nsc.welt.keys():
	l=list()
	for p in nsc.welt[kl]:
		l.append(p.features)
	nsc.welt[kl]=l
	g.replot(Gnuplot.Data(nsc.welt[kl], title=kl, cols=(0,1)))

graph_file_name='-'.join((os.path.splitext(ifile_name)[0], "mvc.ps"))
#raw_input('press enter to write plot %r\n' % (graph_file_name))
g.hardcopy(graph_file_name, color=1)


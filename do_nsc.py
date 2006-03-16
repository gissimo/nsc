#! /usr/bin/env python -O

import os, sys
import getopt 
import Gnuplot
import nsc

klasse_index=0
separator=None

if len(sys.argv) == 1:
	print '\nusage: %s filename [-p prototypes file], [--separator char]\n' % (sys.argv[0])
	sys.exit()

arguments=getopt.gnu_getopt(sys.argv[1:], 'p:', ('separator=', 'classid='))
unseen_filename=arguments[1][0]
protos_filename=None

arguments=arguments[0]
for i in range(len(arguments)):
	if arguments[i][0] == '-p':
		protos_filename=arguments[i][1]
	elif arguments[i][0] == '--separator':
		separator=arguments[i][1]
	elif arguments[i][0] == '--classid':
		klasse_index=int(arguments[i][1])

unseen_set=set()
protos_set=set()

n=0
ufile=file(unseen_filename, 'r')
for line in ufile.readlines():
	line=line.split(separator)
	del line[klasse_index]		### needed for testing
	nsc.dim=len(line)
	unseen_set.add(nsc.punkt([float(i) for i in line], None))	## se alcuni punti hanno le stesse coordinate, non li inserisce piu' volte
	n+=1
ufile.close
print n, len(unseen_set)

pfile=file(protos_filename, 'r')
for line in pfile.readlines():
	line=line.split()
	klasse=line[0].strip()
	del line[0]
	protos_set.add(nsc.punkt([float(i) for i in line], klasse))
pfile.close
print len(protos_set)

klassified=nsc.nsc(protos_set, unseen_set)

ofile_name='-'.join((os.path.splitext(unseen_filename)[0], "nsc.txt"))
ofile=file(ofile_name, 'w')
for kl in klassified.keys():
	for point in klassified[kl]:
		ofile.write(''.join((point.__str__(), '\n')))
ofile.close()


#raw_input('press enter to view plot...\n')
g=Gnuplot.Gnuplot(debug=0)
g.title('NSC applied to %r with prototypes from %r' % (unseen_filename.split(os.sep)[-1], protos_filename.split(os.sep)[-1]))
#g.xlabel('')
#g.ylabel('')

protos_dict={}
for p in protos_set:
	if not protos_dict.has_key(p.klasse):
		protos_dict.setdefault(p.klasse, list())
	protos_dict[p.klasse].append(p.features)

for kl in klassified.keys():
	l=list()
	for p in klassified[kl]:
		l.append(p.features)
	klassified[kl]=l
	g.replot(Gnuplot.Data(klassified[kl], title=kl, cols=(0,1)))

graph_file_name='-'.join((os.path.splitext(unseen_filename)[0], "nsc.ps"))

for kl in protos_dict.keys():
	g.replot(Gnuplot.Data(protos_dict[kl], title='**%s**' % (kl), cols=(0,1)))

#raw_input('press enter to write plot %r\n' % (graph_file_name))
g.hardcopy(graph_file_name, color=1)


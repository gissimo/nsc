#!/usr/bin/env python
import math
import random
import mvc
import os, sys
import Gnuplot
import string
from sets import Set

#for i in range(201):
#	punto=mvc.punkt( (random.uniform(-100, 100), random.uniform(-100, 100)), i)
#	mvc.welt.add(punto)

dim=2

sfile=file(sys.argv[1])
for str in sfile.readlines():
	#print str
	l=string.split(str)
	#print l
	for i in range(1, dim+1):
		l[i]=string.atof(l[i])
	#print l[1:dim+1], l[0]
	if not mvc.welt.has_key(l[0]):
		mvc.welt.setdefault(l[0], Set(()))
	mvc.welt[l[0]].add(mvc.punkt((l[1:dim+1]), l[0]))
#	print len(mvc.welt)
#for p in mvc.welt:
#	print p
sfile.close()

eMax=16
noChangeMax=eMax**(0.5) #20
k=3
q=1
sigmaQuadMax=80

#print 'eMax:', eMax, ', noChangeMax:', noChangeMax, ', k:', k, ', q:', q, ', sigmaQuadMax:', sigmaQuadMax

#print 'pass, epoch, lastChange, clusters involved'
result={}
for kl in mvc.welt.keys():
	tmp=mvc.nsc(dim, eMax, noChangeMax, k, q, mvc.welt[kl], sigmaQuadMax)
	if not result.has_key(kl):
		result.setdefault(kl, list())
	for pr in tmp:
		if not pr.isVoid():
			result[kl].append(pr.centre.features)

g=Gnuplot.Gnuplot(debug=0)
g.title('prova')

for kl in result.keys():
	if len(result[kl]) == 0:
		continue
	g.replot(result[kl])
for kl in mvc.welt.keys():
	l=list()
	for p in mvc.welt[kl]:
		l.append(p.features)
	mvc.welt[kl]=l
	g.replot(mvc.welt[kl])


#all=list()
#c=list()
#for kk in tmp:
#	if kk.isVoid():
#		continue
#	kl=list()
#	for point in kk.points:
#		kl.append(point.features)
#	all.append(kl)
#	c.append(kk.centre.features)

#for i in range(len(all)):
#g('set style data boxes')
#g.plot(c)
#g('set style data points')
#for i in range(len(all)):
#	g.replot(all[i])
#g.replot(c)


#!/usr/bin/env python
import random
import mvc

for i in range(101):
	mvc.welt.add(mvc.punkt( (random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(-100, 100)), i))
print 'welt created!'

dim=3
eMax=10
noChangeMax=20
k=3
q=1
sigmaQuadMax=5000

print 'eMax:', eMax, ', noChangeMax:', noChangeMax, ', k:', k, ', q:', q, ', sigmaQuadMax:', sigmaQuadMax

print 'pass, epoch, lastChange, clusters involved'
tmp=mvc.nsc(dim, eMax, noChangeMax, k, q, mvc.welt, sigmaQuadMax)
for p in tmp:
	if not p.isVoid():
		print p


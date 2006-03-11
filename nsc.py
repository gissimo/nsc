"""Nearest subclass classifier (Cor J. Veenman, Marcel J.T. Reinders) implementation essay"""

import math	#sqrt, floor, etc...
import os	#needed for maxint
import random

dim=0
k=3
q=1
eMax=20	#100
noChangeMax=10

welt={}
### keys are klasses, values a set of punkts of that klasse
rank_list={}
### keys are punkts, values the rank list for that punkt

class punkt:
	"""defines a point in n-dimensions Euclidian space, contains:
features
klasse"""

	def __init__(self, features, klasse):
		self.features=tuple(features)
		self.klasse=klasse

	def __eq__(self, other):
		if isinstance(other, punkt):
			for i in xrange(dim):
				if self.features[i] != other.features[i]:
					return False
			if self.klasse == other.klasse:
				return True
		return False

	def __ne__(self, other):
		return not(__eq__(self, other))

	def __hash__(self):
		return hash(self.klasse)^hash(self.features)

	def __repr__(self):
		representation=' '.join(['%.8f' % (i) for i in self.features])
		return '\t'.join((self.klasse.__str__(), representation))

	__str__=__repr__

def distance(first, second):
	"""returns the Euclidian distance between first and second"""
	dist=0
	for i in xrange(dim):
		dist+=(first.features[i]-second.features[i])**2
	return math.sqrt(dist)


class kluster:
	"""a cluster of points of the same class, contains:
points
IB
ib
OB
ob
mean
variance
klasse"""

	def __init__(self, p=None):
		self.points=set()
		self.IB=set()
		self.OB=set()
		if p == None:
			self.flush()
			return
		self.points.add(p)
		self.mean=punkt(p.features, p.klasse)
		self.variance=0.0
		self.klasse=p.klasse
		self.ib=0
		self.IB.add(p)
		self.ob=0
		self.updOB()

	def flush(self):
		self.points.clear()
		self.variance=0.0
		self.klasse=None
		self.mean=punkt(tuple([None for x in xrange(dim)]), None)
		self.IB.clear()
		self.ib=0
		self.OB.clear()
		self.ob=0

	def __repr__(self):
		return 'len: %s, sigma: %s, mean: %s' % (len(self.points), self.variance, self.mean)

	__str__=__repr__

	def isVoid(self):
		if len(self.points) == 0:
			return True
		return False

	def updMean(self):
		self.mean.features=list(self.mean.features)
		for i in xrange(dim):
			self.mean.features[i]=0
			for p in self.points:
				self.mean.features[i]+=(p.features[i])
			self.mean.features[i]=self.mean.features[i].__float__()/len(self.points)
		self.mean.features=tuple(self.mean.features)

	def updVariance(self):
		self.variance=0.0
		for p in self.points:
			for i in xrange(dim):
				self.variance+=(p.features[i]-self.mean.features[i])**2
		self.variance=self.variance.__float__()/len(self.points)

	def updIB(self):
		self.IB.clear()
		for p in self.points:
			limit=0
			for elem in reversed(rank_list[p]):
				if limit < q and elem[1] in self.points:
					self.IB.add(elem[1])
					limit+=1
		self.ib=math.floor(math.sqrt(len(self.IB))).__int__()

	def updOB(self):
		self.OB.clear()
		outer_space=welt[self.klasse].difference(self.points)
		for p in self.points:
			limit=0
			for elem in rank_list[p]:	##se ci sono doppioni nel training set, qui da' KeyError!!!
				if limit < k and elem[1] in outer_space:
					self.OB.add(elem[1])
					limit+=1
		self.ob=math.floor(math.sqrt(len(self.OB))).__int__()

	def add(self, p):
		if len(self.points) == 0:
			self.__init__(p)
			return
		self.points.add(p)
		self.updMean()
		self.updVariance()
		self.updIB()
		self.updOB()

	def multiadd(self, other):		## remember that this does not update kluster's klasse
		self.points.update(other.points)
		self.updMean()
		self.updVariance()
		self.updIB()
		self.updOB()

	def rem(self, p):
		if len(self.points) == 1:
			self.flush()
			return
		self.points.remove(p)
		self.updMean()
		self.updVariance()
		self.updIB()
		self.updOB()

def randomSubset(border, cardinality):
	"""returns an arbitrary set of the given cardinality that is subset of border"""
	Y=set()
	X=set(border)
	limit=min(cardinality, len(X))
	for i in xrange(limit):
		Y.add(X.pop())
	return Y
	#return set(random.SystemRandom.sample(random.SystemRandom(os.urandom(4)), border, cardinality))

def furthest(Y, mean):
	"""the punkt of Y that is furthest from mean"""
	rl=list()
	for p in Y:
		t=distance(mean, p), p
		rl.append(t)
	return max(rl)[1]

def jointVariance(Ca, Cb):
	"""joint variance between Ca and Cb"""
	Cu=kluster()
	Cu.points.update(Ca.points.union(Cb.points))
	Cu.updMean()
	Cu.updVariance()
	return Cu.variance

def gain(Ca, Cb, x):
	"""the variance gain obtained if moving x from Cb to Ca"""
	first=kluster()
	first.points.update(Ca.points)
	first.updMean()
	first.updVariance()
	second=kluster()
	second.points.update(Cb.points)
	second.updMean()
	second.updVariance()
	gab=0
	gab+=first.variance
	gab+=second.variance
	first.points.add(x)
	first.updMean()
	first.updVariance()
	gab-=first.variance
	second.points.remove(x)
	if len(second.points) != 0:
		second.updMean()
		second.updVariance()
		gab-=second.variance
	return gab


def computeRLs(welt_kl):
	"""computes rank lists for each point in welt_kl"""
	for star in welt_kl:
		if not rank_list.has_key(star):
			rank_list.setdefault(star, list())
		for figurant in welt_kl:
			if figurant == star:
				continue
			rank_list[star].append((distance(star, figurant), figurant))
			#d=distance(star, figurant)
			#if d < dMax:
			#	rank_list[star].append((d, figurant))
		rank_list[star].sort()


def mvc(welt_kl, sigmaQuadMax):
	"""Maximum variance cluster"""
	prototypes=set()
	for xi in welt_kl:
		prototypes.add(kluster(xi))

	epoch=lastChange=0
	while (epoch-lastChange < noChangeMax):
		epoch+=1
		for Ca in prototypes:
			if Ca.isVoid():
				continue
			### ISOLATION ###
			if Ca.variance > sigmaQuadMax and epoch < eMax:
				Y=randomSubset(Ca.IB, Ca.ib)
				x=furthest(Y, Ca.mean)
				#print '%s: ISOLATION, %d' % (Ca.klasse, epoch)
				Ca.rem(x)
				for Cm in prototypes:
					if Cm == Ca:
						continue	# ovviamente se ne cerca un altro
					if Cm.isVoid():
						Cm.add(x)
						break		# trovato uno vuoto allora e' tutto ok e si termina
				continue
			### UNION ###
			if Ca.variance <= sigmaQuadMax:
				sMin=os.sys.maxint
				Cm=None
				for Cb in prototypes:
					if (len(Ca.OB.intersection(Cb.points)) != 0) and (Ca != Cb):
						jv=jointVariance(Ca, Cb)
						if (jv <= sigmaQuadMax) and (jv < sMin):
							sMin=jv
							Cm=Cb
				if Cm != None:
					#print '%s: UNION, %d' % (Ca.klasse, epoch)
					Ca.multiadd(Cm)
					Cm.flush()
					lastChange=epoch
					continue
			### PERTURBATION ###
			Y=randomSubset(Ca.OB, Ca.ob)
			gMax=-os.sys.maxint-1
			Cm=None
			xMax=None
			for x in Y:
				for Cb in prototypes:
					if Cb == Ca:
						continue
					if x in Cb.points:
						g=gain(Ca, Cb, x)
						if g > gMax:
							gMax=g
							Cm=Cb
							xMax=x
			if gMax > 0:
				#print '%s: PERTURBATION, %d' % (Ca.klasse, epoch)
				Ca.add(xMax)
				Cm.rem(xMax)
				lastChange=epoch
	#print 'last run at %d' % (epoch)
	return prototypes


def nsc(prototypes, unclassified):
	"""Nearest subclass classifier"""
	classified={}
	for p in unclassified:
		relative_distances=list()
		for proto in prototypes:
			t=distance(p, proto), proto.klasse
			relative_distances.append(t)
		p.klasse=min(relative_distances)[1]	#ValueError: min() arg is an empty sequence
		if not classified.has_key(p.klasse):
			classified.setdefault(p.klasse, set())
		classified[p.klasse].add(p)
	return classified


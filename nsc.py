"""Nearest subclass classifier (Cor J. Veenman, Marcel J.T. Reinders)
implementation essay"""

import sys, os
from math import sqrt as _sqrt, floor as _floor
from random import sample as _sample
if sys.version_info[0:2] < (2, 4):
	from sets import Set as set, ImmutableSet as frozenset


dim=0	### external programs should set this
k=3
q=1
eMax=20	### 100 is suggested by the authors of NSC
noChangeMax=10

welt={}
### keys are class labels, values a set of points of that label
### this is necesasry due to the pre-supervised nature of the algorithm
rank_list={}
### keys are points, value the rank list for the given point


class punkt:
	"""defines a point in n-dimensions Euclidian space, contains:
	features, klasse."""

	def __init__(self, features, klasse):
		"""initializes the point"""
		self.features=tuple(features)
		self.klasse=klasse

	def __eq__(self, other):
		"""determines if two instances of point are identical.
		two points are different if are different either the features or
		the class label."""
		if isinstance(other, punkt):
			for i in xrange(dim):
				if self.features[i] != other.features[i]:
					return False
			if self.klasse == other.klasse:
				return True
		return False

	def __ne__(self, other):
		"""determines if two instances of point are different"""
		return not(__eq__(self, other))

	def __hash__(self):
		"""hashes the point (needed to inserting it in sets or dictionaries)"""
		return hash(self.klasse)^hash(self.features)

	def __repr__(self):
		"""representation of the point"""
		representation=' '.join(['%.8f' % (i) for i in self.features])
		return '%s\t%s' % (self.klasse.__str__(), representation)

	__str__=__repr__

def distance(first, second):
	"""returns the Euclidian distance between two points"""
	dist=0
	for i in xrange(dim):
		dist+=(first.features[i]-second.features[i])**2
	return _sqrt(dist)


class kluster:
	"""a cluster of points of the same class, contains:
	points, IB, ib, OB, ob, mean, variance, klasse.
	each and every operation on the cluster's content maintains the cluster's 
	consistency"""

	def __init__(self, p=None):
		"""initializes the cluster with a point or, if p is None, as void"""
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
		"""deletes all points of the cluster"""
		self.points.clear()
		self.variance=0.0
		self.klasse=None
		self.mean=punkt(tuple([None]*dim), None)	### the punkt object HAS to
		self.IB.clear()								### be ALWAYS a tuple() of
		self.ib=0									### the RIGHT length
		self.OB.clear()
		self.ob=0

	def __repr__(self):
		"""representation of the cluster"""
		return 'len: %d, sigma: %.2f, mean: %s' % (len(self.points), self.variance, self.mean)

	__str__=__repr__

	def isVoid(self):
		"""if a cluster is void or not"""
		if len(self.points) == 0:
			return True
		return False

	def updMean(self):
		"""updates the cluster's mean object.
		this should be always run before updating the variance."""
		self.mean.features=[0]*dim	### now is a list() of zeros
		for i in xrange(dim):
			for p in self.points:
				self.mean.features[i]+=(p.features[i])
			self.mean.features[i]=self.mean.features[i].__float__()/len(self.points)
		self.mean.features=tuple(self.mean.features)	### again a tuple()

	def updVariance(self):
		"""updates cluster's variance.
		requires that the mean object is consistent."""
		self.variance=0.0
		for p in self.points:
			for i in xrange(dim):
				self.variance+=(p.features[i]-self.mean.features[i])**2
		self.variance=self.variance.__float__()/len(self.points)

	def updIB(self):
		"""updates the inner border of the cluster.
		for each point inside the cluster scans the related reversed rank list
		for internal points."""
		self.IB.clear()
		for p in self.points:
			limit=0
			if sys.version_info[0:2] >= (2, 4):
				for elem in reversed(rank_list[p]):
					if limit < q and elem[1] in self.points:
						self.IB.add(elem[1])
						limit+=1
			else:
				for i in range(len(rank_list[p]))[::-1]:
					if limit < q and rank_list[p][i][1] in self.points:
						self.IB.add(rank_list[p][i][1])
						limit+=1
		self.ib=_floor(_sqrt(len(self.IB))).__int__()

	def updOB(self):
		"""updates the outer border of the cluster.
		for each point inside the cluster scans the related rank list for
		external points"""
		self.OB.clear()
		outer_space=welt[self.klasse].difference(self.points)
		for p in self.points:
			limit=0
			for elem in rank_list[p]:
				if limit < k and elem[1] in outer_space:
					self.OB.add(elem[1])
					limit+=1
		self.ob=_floor(_sqrt(len(self.OB))).__int__()

	def add(self, p):
		"""adds a point to the cluster"""
		if len(self.points) == 0:
			self.__init__(p)
			return
		self.points.add(p)
		self.updMean()
		self.updVariance()
		self.updIB()
		self.updOB()

	def multiadd(self, other):
		"""adds multiple points to the cluster.
		useful to reduce the number of operations needed to maintan the 
		consistency.
		note that this does not update cluster's label."""
		self.points.update(other.points)
		self.updMean()
		self.updVariance()
		self.updIB()
		self.updOB()

	def rem(self, p):
		"""removes a point from the cluster"""
		if len(self.points) == 1:
			self.flush()
			return
		self.points.remove(p)
		self.updMean()
		self.updVariance()
		self.updIB()
		self.updOB()

def randomSubset(border, cardinality):
	"""returns an arbitrary set of the given cardinality that is subset of
	border"""
	#Y=set()
	#X=set(border)					### this can avoid strange things in the
	#limit=min(cardinality, len(X))	### case that random goes crazy
	#for i in xrange(limit):
	#	Y.add(X.pop())		### set.pop() is not truly random
	#return Y
	return set(_sample(border, cardinality))	### this IS random!

def furthest(Y, mean):
	"""the point of Y that is furthest from the point mean"""
	rl=list()		### cannot use the rank list for mean because mean
	for p in Y:		### is not necessarily part of the training set
		t=distance(mean, p), p
		rl.append(t)
	return max(rl)[1]

def jointVariance(Ca, Cb):
	"""joint variance of Ca and Cb"""
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


def computeRLs(kl):
	"""computes rank lists for each point in welt[kl]"""
	for star in welt[kl]:
		if not rank_list.has_key(star):
			rank_list.setdefault(star, list())
		for figurant in welt[kl]:
			if figurant == star:
				continue
			rank_list[star].append((distance(star, figurant), figurant))
		rank_list[star].sort()


def mvc(kl, sigmaQuadMax):
	"""Maximum variance cluster algorithm"""
	prototypes=set()
	for xi in welt[kl]:
		prototypes.add(kluster(xi))

	epoch=lastChange=0
	while epoch-lastChange < noChangeMax:
		epoch+=1
		for Ca in prototypes:
			if Ca.isVoid():
				continue
			### ISOLATION PASS ###
			if Ca.variance > sigmaQuadMax and epoch < eMax:
				Y=randomSubset(Ca.IB, Ca.ib)
				x=furthest(Y, Ca.mean)
				#print '%s: ISOLATION, %d' % (Ca.klasse, epoch)
				Ca.rem(x)
				for Cm in prototypes:	### searching for a void cluster
					if Cm == Ca:
						continue
					if Cm.isVoid():
						Cm.add(x)
						break
				continue	### if the isolation pass is taken
							### choose another cluster
			### UNION PASS ###
			if Ca.variance <= sigmaQuadMax:
				sMin=os.sys.maxint
				Cm=None
				for Cb in prototypes:
					if Cb == Ca:
						continue
					if len(Ca.OB.intersection(Cb.points)) != 0:
						jv=jointVariance(Ca, Cb)
						if (jv <= sigmaQuadMax) and (jv < sMin):
							sMin=jv
							Cm=Cb
				if Cm != None:
					#print '%s: UNION, %d' % (Ca.klasse, epoch)
					Ca.multiadd(Cm)
					Cm.flush()
					lastChange=epoch
					continue	### if the union pass is taken
								### choose another cluster
			### PERTURBATION PASS ###
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
	classified=set()
	for p in unclassified:
		relative_distances=list()
		for proto in prototypes:
			relative_distances.append((distance(p, proto), proto.klasse))
		p.klasse=min(relative_distances)[1]
		classified.add(p)
	return classified

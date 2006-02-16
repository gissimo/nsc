"""Maximum variance cluster (Cor J. Veenman, Marcel J.T. Reinders) implementation essay"""

from __future__ import division	#needed for int/int -> float
#from sets import Set
import math	#sqrt, floor, etc...
import copy	#needed to set the centre when creating the cluster
import os	#needed for maxint
import string

dim=0
k=3
q=1
eMax=100
noChangeMax=10

welt={}

class punkt:
	"""defines a point in n-dimensions Euclidian space with features vector and a class"""
	#features
	#klasse

	def __init__(self, features, klasse):
		self.features=tuple(features[0:dim])
		self.klasse=klasse
	
	def __eq__(self, other):
		if isinstance(other, punkt):
			for i in range(dim):
				if self.features[i] != other.features[i]:
					return False
			if self.klasse == other.klasse:
				return True
		return False

	def __ne__(self, other):
		return not(__eq__(self, other))

	def __hash__(self):
		result=0
		for i in range(dim):
			result^=hash(self.features[i])
		result^=hash(self.klasse)
		return result
		
	def __repr__(self):
		#return '%r %r' % (self.features, self.klasse)
		#return '%r' % (self.features, )
		representation=self.klasse.__str__()
		for i in range(dim):
			representation=string.join((representation, '%.8f' % self.features[i]), sep='\t')
		return representation

	__str__=__repr__


def distance(first, second):
	dist=0
	for i in range(dim):
		dist+=(first.features[i]-second.features[i])**2
	return math.sqrt(dist)


class kluster:
	"""a cluster of points of the same class with built-in centre, variance, inner and outer border"""
	#points
	#IB
	#ib
	#OB
	#ob
	#centre
	#varianz
	#klasse

	def __init__(self, punto=None):
		self.points=set()
		self.IB=set()
		self.OB=set()
		if punto == None:
			self.centre=punkt((None, ), None)
			self.flush()
			return
		self.points.add(punto)
		self.centre=copy.deepcopy(punto)
		self.varianz=0.0
		self.klasse=punto.klasse
		self.ib=0
		self.IB.add(punto)
		self.ob=0
		self.updOB()
	
	def flush(self):
		self.points.clear()
		self.varianz=0.0
		self.klasse=None
		self.centre=punkt((None, ), None)
		self.IB.clear()
		self.ib=0
		self.OB.clear()
		self.ob=0

	def __repr__(self):
		return 'len: %r, sigma: %r, centre: %r' % (len(self.points), self.varianz, self.centre.features)

	__str__=__repr__

	def isVoid(self):
		if len(self.points) == 0:
			return True
		else:
			return False

	def updCentre(self):
		temp=list()
		for i in range(dim):
			temp.append(0)
			for p in self.points:
				temp[i]+=(p.features[i])
			temp[i]/=len(self.points)
		self.centre.features=tuple(temp[0:dim])

	def updVariance(self):
		self.varianz=0.0
		for p in self.points:
			for i in range(dim):
				self.varianz+=(p.features[i]-self.centre.features[i])**2
			#self.varianz/=len(self.points)	############################

	def updIB(self):
		self.IB.clear()
		for f in self.points:
			relative_distances=list()
			for s in self.points:
				t=distance(f, s), s
				relative_distances.append(t)
			for i in range(min(q, len(relative_distances))):
				M=max(relative_distances)
				relative_distances.remove(M)
				self.IB.add(M[1])
		self.ib=math.floor(math.sqrt(len(self.IB))).__int__()

	def updOB(self):
		self.OB.clear()
		outer_space=welt[self.klasse].difference(self.points)
		for f in self.points:
			relative_distances=list()
			for s in outer_space:
				t=distance(s, f), s
				relative_distances.append(t)
			for i in range(min(k, len(relative_distances))):
				m=min(relative_distances)
				relative_distances.remove(m)
				self.OB.add(m[1])
		self.ob=math.floor(math.sqrt(len(self.OB))).__int__()

	def add(self, p):
		if len(self.points) == 0:
			self.__init__(p)
			return
		self.points.add(p)
		self.updCentre()
		self.updVariance()
		self.updIB()
		self.updOB()

	def multiadd(self, other):
		self.points.update(other.points)
		self.updCentre()
		self.updVariance()
		self.updIB()
		self.updOB()
	
	def rem(self, p):
		self.points.remove(p)
		if len(self.points) == 0:
			self.flush()
			return
		self.updCentre()
		self.updVariance()
		self.updIB()
		self.updOB()
		return


def randomSubset(border, cardinality):
	limit=min(cardinality, len(border))
	fr=set(border)
	Y=set()
	for i in range(limit):
		Y.add(fr.pop())				# il pop non va bene perche' elimina l'elemento e forse non e' proprio random

	return Y

def furthest(Y, centre):
	l=list()
	for p in Y:
		t=distance(centre, p), p
		l.append(t)
	return max(l)[1]

def jointVariance(Ca, Cb):
	Cu=kluster()
	Cu.points.update(Ca.points.union(Cb.points))
	Cu.updCentre()
	Cu.updVariance()
	return Cu.varianz

def gain(Ca, Cb, x):
	first=kluster()
	first.points.update(Ca.points)
	first.updCentre()
	first.updVariance()
	second=kluster()
	second.points.update(Cb.points)
	second.updCentre()
	second.updVariance()
	gab=0
	gab+=first.varianz
	gab+=second.varianz
	first.points.add(x)
	first.updCentre()
	first.updVariance()
	second.points.remove(x)
	if len(second.points) != 0:
		second.updCentre()
		second.updVariance()
		gab-=second.varianz
	gab-=first.varianz
	return gab


def mvc(welt, sigmaQuadMax):
	prototypes=set()
	for xi in welt:
		prototypes.add(kluster(xi))
	
	epoch=lastChange=0
	while (epoch-lastChange < noChangeMax):
		epoch+=1
		for Ca in prototypes:
			if Ca.isVoid():
				continue
			### ISOLATION ###
			if Ca.varianz > sigmaQuadMax and epoch < eMax:
				Y=randomSubset(Ca.IB, Ca.ib)
				x=furthest(Y, Ca.centre)
				print '%s: ISOLATION, %d' % (Ca.klasse, epoch)
				Ca.rem(x)
				for Cm in prototypes:
					if Cm == Ca:
						continue	# ovviamente se ne cerca un altro
					if Cm.isVoid():
						Cm.add(x)
						break		# trovato uno vuoto allora e' tutto ok e si termina
				continue
			### UNION ###
			if Ca.varianz <= sigmaQuadMax:
				sMin=os.sys.maxint
				Cm=None
				for Cb in prototypes:
					if (len(Ca.OB.intersection(Cb.points)) != 0) and (Ca != Cb):
						jv=jointVariance(Ca, Cb)
						if (jv <= sigmaQuadMax) and (jv < sMin):
							sMin=jv
							Cm=Cb
				if Cm != None:
					print '%s: UNION, %d' % (Ca.klasse, epoch)
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
				print '%s: PERTURBATION, %d' % (Ca.klasse, epoch)
				Ca.add(xMax)
				Cm.rem(xMax)
				lastChange=epoch
	print 'last run at %d' % (epoch)
	return prototypes


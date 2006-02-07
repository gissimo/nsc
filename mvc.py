# -*- coding: utf-8 -*-
"""Maximum variance cluster (Cor J. Veenman, Marcel J.T. Reinders) implementation essay"""

from __future__ import division	#needed for int/int -> float
from sets import Set
import math
import copy	#needed to set the centre when creating the cluster
import os

dim=3
k=3	#elements of outer border
q=1	#elements of inner border
#eMax=100
#noChangeMax=
#sigmaQuadMax=
welt=Set()

class punkt:
	"""defines a point in n-dimensions Euclidian space with features vector and a class"""
	#features
	#klasse

	def __init__(self, features, klasse):
		self.features=tuple(features[0:dim])
		self.klasse=klasse
	
	def __repr__(self):
		"""prints feaure vector and class"""
		return '%r %r' % (self.features, self.klasse)

	__str__=__repr__

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


def distance(first, second):
	dist=0
	for i in range(dim):
		dist+=(first.features[i]-second.features[i])**2
	return math.sqrt(dist)


class kluster:
	"""a cluster of points of the same class with built-in centre, variance, inner and outer border"""
	#points=Set()
	#IB=Set()
	#ib=0
	#OB=Set()
	#ob=0
	#centre=punkt()
	#varianz=int(0)
	#klasse=''

	def __init__(self, punto):
		self.points=Set()
		self.points.add(punto)
		self.centre=copy.copy(punto)
		self.varianz=0.0
		self.klasse=punto.klasse
		self.IB=Set()
		self.ib=0
		self.IB.add((0, punto))
		self.OB=Set()
		self.ob=0
		self.updOB()
	
	def __repr__(self):
		return 'class: %r, len: %r, sigma: %r, centre: %r' % (self.klasse, len(self.points), self.varianz, self.centre.features)

	__str__=__repr__

	def updCenter(self):
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

	def isVoid(self):
		if len(self.points) == 0:
			return True
		else:
			return False

	def updIB(self):
		relative_distances=list()
		for p in self.points:
			t=distance(p, self.centre), p
			relative_distances.append(t)
		relative_distances.sort()
		relative_distances.reverse()
		self.IB.clear()
		#for i in range(q):
		#	self.IB.add(relative_distances[i])
		self.IB.update(relative_distances[0:q])
		self.ib=math.floor(math.sqrt(len(self.IB))).__int__()
	
	def randomSubset(self, border, cardinality):
		Y=Set()
		tmp=list()
		limit=min(cardinality, len(border))
		for i in range(limit):
			tmp.append(border.pop())
		#for i in range(limit):
		#	border.add(tmp[i])
		#	Y.add(tmp[i])
		border.update(tmp[0:limit])
		Y.update(tmp[0:limit])
		return Y

	def furthest(self):
		l=list()
		for p in self.randomSubset(self.IB, self.ib):
			l.append(p)
		l.sort()
		l.reverse()
		return l[0][1]

	def updOB(self):
		self.OB.clear()
		outer_space=welt.difference(self.points)
		limit=min(len(outer_space), k)
		#print 'outer', len(outer_space)	####
		r=0.2
		while (len(self.OB) < limit):		##QUI SI VA IN LOOP!!! (e se non si arriva a k elementi???)
			#print 'r',r, 'len',len(self.OB)	####
			n=None
			for p in outer_space:
				#print 'p',p	####
				d=distance(p, self.centre)
				#print 'd',d, 'r',r, 'len',len(self.OB)	####
				#if ( (d < r) & (len(self.OB) < k) ):
				if (d < r) and (len(self.OB) < k):
					#print 'true'
					self.OB.add(p)
					n=p
			outer_space.discard(n)
			#outer_space.difference_update(self.OB)
			#for p in self.OB:
			#	outer_space.discard(p)
			r+=0.2
		self.ob=math.floor(math.sqrt(len(self.OB))).__int__()

	def add(self, p):
		self.points.add(p)
		if len(self.points) == 1:
			self.klasse=p.klasse
			self.centre=copy.copy(p)
			self.varianz=0
			self.IB.add((0, p))
			self.ib=0
		else:
			self.updVariance()
			self.updCenter()
			self.updIB()
		self.updOB()
	
	def rem(self, p):
		self.points.discard(p)
		if len(self.points) == 0:
			self.flush()
			return
		self.updCenter()
		self.updVariance()
		self.updIB()
		self.updOB()
		return

	def flush(self):
		self.points.clear()
		self.varianz=0.0
		self.centre.klasse=None
		temp=list()
		for i in range(dim):
			temp.append(None)
		self.centre.features=tuple(temp[0:dim])
		self.klasse=None
		self.IB.clear()
		self.ib=0
		self.OB.clear()
		self.ob=0


def jointVariance(Ca, Cb):
	Cu=copy.deepcopy(Ca)
	#Cu.points=Cu.points.union(Cb.points)
	Cu.points.union_update(Cb.points)
	Cu.updCenter()
	Cu.updVariance()
	return Cu.varianz

def gain(Ca, Cb, x):
	first=copy.deepcopy(Ca)
	second=copy.deepcopy(Cb)
	gab=0
	gab+=first.varianz
	gab+=second.varianz
	first.add(x)
	second.rem(x)
	gab-=first.varianz
	gab-=second.varianz
	return gab


def nsc(dim, eMax, noChangeMax, k, q, w, sigmaQuadMax):	# quando esegue sia isolation che union (indipendentemente
	welt=copy.deepcopy(w)								# da perturbation) quasi sempre abbiamo un cluster con
	print 'welt copied'
	prototypes=Set()									# varianza > sigmaQuadMax, verificare.
	
	for xi in welt:
		prototypes.add(kluster(xi))
		print xi
	print 'base prototypes created!'
	
	epoch=lastChange=0
	while (epoch-lastChange < noChangeMax):
		epoch+=1
		for Ca in prototypes:
			if Ca.isVoid():
				continue
			#if ( (Ca.varianz > sigmaQuadMax) & (epoch < eMax) ):		# Isolation #
			if (Ca.varianz > sigmaQuadMax) and (epoch < eMax):        # Isolation #
				print 'ISOLATION', epoch, lastChange, Ca.klasse
				x=Ca.furthest()
				Ca.rem(x)
				for Cm in prototypes:
					if Cm == Ca:
						continue
					if Cm.isVoid():
						Cm.add(x)
						break		# gestire il caso in cui non trova cluster vuoti (?)
			elif Ca.varianz <= sigmaQuadMax:		# Union #
				sMin=os.sys.maxint		# si può utilizzare maxfloat???
				Cm=None
				for Cb in prototypes:
					if (len(Ca.OB.intersection(Cb.points)) != 0) and (Ca != Cb):
						jv=jointVariance(Ca, Cb)
						if (jv <= sigmaQuadMax) and (jv < sMin):
							sMin=jv
							Cm=Cb
				if Cm != None:
					print 'UNION', epoch, lastChange, Ca.klasse, '<-', Cm.klasse
					for p in Cm.points:		#
						Ca.add(p)			# forse è meglio aggiungere i punti tutti in una volta con op su insiemi
					Cm.flush()				# (magari con una points.update() ???)	# vedi todo n° 1
					lastChange=epoch
			else:		# Perturbation #
				Y=Ca.randomSubset(Ca.OB, Ca.ob)
				gMax=-os.sys.maxint-1	# si può utilizzare minfloat???
				Cm=None
				xMax=None
				for x in Y:
					for Cb in prototypes:
						if x in Cb.points:
							g=gain(Ca, Cb, x)
							if g > gMax:
								gMax=g
								Cm=Cb
								xMax=x
				if gMax > 0:
					print 'PERTURBATION', epoch, lastChange, Ca.klasse, '<-', Cm.klasse
					Ca.add(xMax)
					Cm.rem(xMax)
					lastChange=epoch
	print 'last run at epoch:', epoch
	return prototypes


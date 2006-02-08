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
		"""prints feaure vector and class"""
		return '%r %r' % (self.features, self.klasse)

	__str__=__repr__


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
		self.centre=copy.deepcopy(punto)
		self.varianz=0.0
		self.klasse=punto.klasse
		self.IB=Set()
		self.ib=0
		self.IB.add(punto)
		self.OB=Set()
		self.ob=0
		self.updOB()
	
	def __repr__(self):
		return 'class: %r, len: %r, sigma: %r, centre: %r' % (self.klasse, len(self.points), self.varianz, self.centre.features)

	__str__=__repr__

	def isVoid(self):
		if len(self.points) == 0:
			return True
		else:
			return False

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

	def updIB(self):
		self.IB.clear()
		for f in self.points:
			relative_distances=list()
			for s in self.points:
				#if f == s:
				#	break
				t=distance(f, s), s
				relative_distances.append(t)
			relative_distances.sort()
			relative_distances.reverse()
			#self.IB.update(relative_distances[0:q])
			for i in range( min(q, len(relative_distances)) ):
				self.IB.add(relative_distances[i][1])
		self.ib=math.floor(math.sqrt(len(self.IB))).__int__()

	def updOB(self):
		self.OB.clear()
		outer_space=welt.difference(self.points)
		#print 'len(outer_space):', len(outer_space)
		for f in self.points:
			relative_distances=list()
			for s in outer_space:
				t=distance(s, f), s
				relative_distances.append(t)
			relative_distances.sort()
			for i in range( min(k, len(relative_distances)) ):
				#print relative_distances[i][1]
				self.OB.add(relative_distances[i][1])
		self.ob=math.floor(math.sqrt(len(self.OB))).__int__()
		#print 'len(OB):', len(self.OB), 'len(points):', len(self.points)
		#print self.OB

	def add(self, p):
		self.points.add(p)
		if len(self.points) == 1:
			self.klasse=copy.deepcopy(p.klasse)
			self.centre=copy.deepcopy(p)
			self.varianz=0
			self.IB.add(p)
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
		self.klasse=None
		self.centre.klasse=None
		temp=list()
		for i in range(dim):
			temp.append(None)
		self.centre.features=tuple(temp[0:dim])
		self.IB.clear()
		self.ib=0
		self.OB.clear()
		self.ob=0


def randomSubset(border, cardinality):		#portare fuori dalla classe ???
	fr=copy.deepcopy(border)
	Y=Set()
	#tmp=list()
	limit=min(cardinality, len(fr))
	for i in range(limit):
		Y.add(fr.pop())
	#for i in range(limit):
	#	border.add(tmp[i])
	#	Y.add(tmp[i])
	#border.update(tmp[0:limit])
	#Y.update(tmp[0:limit])
	return Y

def furthest(Y, centre):
	l=list()
	for p in Y:
		t=distance(centre, p), p
		l.append(t)
	l.sort()
	l.reverse()
	return l[0][1]

def jointVariance(Ca, Cb):
	Cu=copy.deepcopy(Ca)				#invece di copiare, creare un nuovo kluster ed aggiungere gli oggetti punkt
	#Cu.points=Cu.points.union(Cb.points)
	Cu.points.union_update(Cb.points)
	Cu.updCenter()
	Cu.updVariance()
	return Cu.varianz

def gain(Ca, Cb, x):
	first=copy.deepcopy(Ca)				#vedi nota in j.v.
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
	#print 'welt copied'
	prototypes=Set()									# varianza > sigmaQuadMax, verificare.
	
	for xi in welt:
		#print xi
		prototypes.add(kluster(xi))
	#print 'base prototypes created!'
	#for Ci in prototypes:
	#	print Ci.OB
	
	epoch=lastChange=0
	while (epoch-lastChange < noChangeMax):
		epoch+=1
		for Ca in prototypes:
			if Ca.isVoid():
				continue
			if (Ca.varianz > sigmaQuadMax) and (epoch < eMax):        # Isolation #
				Y=randomSubset(Ca.IB, Ca.ib)
				x=furthest(Y, Ca.centre)
				print 'ISOLATION', epoch, lastChange, Ca.klasse, '->', x.klasse
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
				Y=randomSubset(Ca.OB, Ca.ob)
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


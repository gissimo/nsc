"""Nearest subclass classifier (Cor J. Veenman, Marcel J.T. Reinders) implementation essay"""

import os	#needed for maxint
from math import sqrt as _sqrt
from math import floor as _floor
from random import sample as _sample

dim=0

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
	return _sqrt(dist)


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
	
	k=3
	q=1
	
	def __init__(self, p=None, world=None, rank_list=None):
		self.points=set()
		self.IB=set()
		self.OB=set()
		if p == None:
			self.flush()
			return
		self.points.add(p)
		self.mean=punkt(p.features, p.klasse)
		self.variance=0.0
		#self.klasse=p.klasse
		if world != None:
			self.world=world
		if rank_list != None:
			self.rank_list=rank_list
		self.ib=0
		self.IB.add(p)
		self.ob=0
		self.updOB()
	
	def flush(self):
		self.points.clear()
		self.variance=0.0
		#self.klasse=None
		self.mean=punkt(tuple([None]*dim), None)
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
		print self.mean

	def updVariance(self):
		self.variance=0.0
		for p in self.points:
			for i in xrange(dim):
				self.variance+=(p.features[i]-self.mean.features[i])**2
		self.variance=self.variance.__float__()/len(self.points)
		print self.varianz

	def updIB(self):
		self.IB.clear()
		for p in self.points:
			limit=0
			for elem in reversed(self.rank_list[p]):
				if limit < self.q and elem[1] in self.points:
					self.IB.add(elem[1])
					limit+=1
		self.ib=_floor(_sqrt(len(self.IB))).__int__()

	def updOB(self):
		self.OB.clear()
		outer_space=self.world.difference(self.points)
		for p in self.points:
			limit=0
			for elem in self.rank_list[p]:	##se ci sono doppioni nel training set, qui da' KeyError!!!
				if limit < self.k and elem[1] in outer_space:
					self.OB.add(elem[1])
					limit+=1
		self.ob=_floor(_sqrt(len(self.OB))).__int__()

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
	#return set(_sample(border, cardinality))

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


class mvc:
	eMax=20
	noChangeMax=10
	
	universe=frozenset()
	welt={}
	### keys are klasses, values a set of punkts of that klasse
	rank_list={}
	### keys are punkts, values the rank list for that punkt
	classified=set()
	prototypes=set()
	
	
	def reset(self):
		self.welt.clear()
		self.rank_list.clear()
		self.classified.clear()
		self.prototypes.clear()
	
	
	def __init__(self, ifile_name, separator, klasse_index=None):
		"""reads punkts from file and fills with them the set universe"""
		self.universe=set(self.universe)
		sfile=file(ifile_name, 'r')
		for line in sfile.readlines():
			line.lstrip()
			if line.startswith('#') or len(line) == 0:	#line is either a comment or empty
				del line
				continue
			line=line.split(separator)
			if klasse_index != None:
				klasse=line[klasse_index].strip()
				del line[klasse_index]
			else:
				klasse=None
			dim=len(line)
			try:		
				self.universe.add(punkt([float(i) for i in line], klasse))
			except ValueError:
				print 'WARNING: unable to understand line: %s' % (line)
				continue
		sfile.close()
		self.universe=frozenset(self.universe)
		if len(self.universe) == 0:
			print '\nno values can be read from %s!\n' % (ifile_name)
			sys.exit()
	
	
	def random_samples(self, n):
		"""computes a list of n random subsets of to_sample"""
		#n=math.floor(math.sqrt(len(to_sample))).__int__()
		#n=10
		step=len(self.universe)/n
		#print len(to_sample)
		lamb=list(self.universe)
		#print len(lamb)
		#random.SystemRandom.shuffle(random.SystemRandom(os.urandom(4)), lamb)
		lamb.reverse()
		#print 'lamb', len(lamb)
		#random.shuffle(lamb)
		self.testing_sets=[None]*n
		for i in xrange(n-1):
			#testing_sets.insert(i, set())
			#testing_sets[i].update(lamb[i:i+step])
			self.testing_sets[i]=frozenset(lamb[i:i+step])
		self.testing_sets[n-1]=frozenset(lamb[(n-1)*step:])
	
	
#	def random_samples(self, n):
#		"""computes a list of n random subsets of to_sample"""
#		dimension=len(to_sample)/n
#		testing_sets=[None]*n
#		lamb=set(to_sample)
#		for i in xrange(n-1):
#			#print dimension
#			temp=frozenset(random.sample(lamb, dimension))
#			#temp=set(random.SystemRandom.sample(random.SystemRandom(os.urandom(4)), lamb, dimension))
#			#print len(temp)
#			testing_sets[i]=temp
#			#lamb.difference_update(temp)
#			lamb=lamb-temp
#			#print len(lamb)
#		testing_sets[n-1]=frozenset(lamb)
#		return testing_sets
#	
#	
#	def random_samples(self, n):
#		"""computes a list of n random subsets of to_sample"""
#		testing_sets=[None]*n
#		td={}
#		for p in to_sample:
#			if not td.has_key(p.klasse):
#				td.setdefault(p.klasse, list([set(), None]))
#			td[p.klasse][0].add(p)
#		
#		for k in td.keys():
#			td[k][1]=len(td[k][0])/n
#			#print 'rsk', len(td[k][0]), td[k][1], k
#		
#		for i in xrange(n-1):
#			testing_sets[i]=set()
#			for k in td.keys():
#				rsk=random.sample(td[k][0], td[k][1])
#				testing_sets[i].update(rsk)
#				td[k][0].difference_update(rsk)
#		testing_sets[n-1]=set()
#		for k in td.keys():
#			testing_sets[n-1].update(td[k][0])
#		return testing_sets
	
	
	def populate_world(self, sample):
		"""fills the welt dictionary with the points from the set sample"""
		for p in sample:
			if not self.welt.has_key(p.klasse):
				self.welt.setdefault(p.klasse, set())
			self.welt[p.klasse].add(p)
	
	
	def computeRLs(self, kl):
		"""computes rank lists for each point in self.welt[kl]"""
		for star in self.welt[kl]:
			if not self.rank_list.has_key(star):
				self.rank_list.setdefault(star, list())
			for figurant in self.welt[kl]:
				if figurant == star:
					continue
				t=tuple([distance(star, figurant), figurant])
				print 'AUUUUUUUUUUUUUUUU!!!', t
				self.rank_list[star].append(t)
			self.rank_list[star].sort()
	
	
	def mvc(self, kl, sigmaQuadMax):
		"""Maximum variance cluster"""
		klusters=set()
		for xi in self.welt[kl]:
			klusters.add(kluster(xi, self.welt[kl], self.rank_list))
		print 'klusters', len(klusters)
		
		epoch=lastChange=0
		while (epoch-lastChange < self.noChangeMax):
			#print 'while', sigmaQuadMax
			epoch+=1
			for Ca in klusters:
				#print 'ciao', Ca.rank_list.values()
				if Ca.isVoid():
					continue
				### ISOLATION ###
				if Ca.variance > sigmaQuadMax and epoch < self.eMax:
					print 'isol'
					Y=randomSubset(Ca.IB, Ca.ib)
					x=furthest(Y, Ca.mean)
					print 'ISOLATION, %d' % (epoch)
					Ca.rem(x)
					for Cm in klusters:
						if Cm == Ca:
							continue	# ovviamente se ne cerca un altro
						if Cm.isVoid():
							Cm.add(x)
							break		# trovato uno vuoto allora e' tutto ok e si termina
					continue
				### UNION ###
				if Ca.variance <= sigmaQuadMax:
					print 'uni'
					sMin=os.sys.maxint
					Cm=None
					for Cb in klusters:
						if (len(Ca.OB.intersection(Cb.points)) != 0) and (Ca != Cb):
							jv=jointVariance(Ca, Cb)
							if (jv <= sigmaQuadMax) and (jv < sMin):
								sMin=jv
								Cm=Cb
					if Cm != None:
						print 'UNION, %d' % (epoch)
						Ca.multiadd(Cm)
						Cm.flush()
						lastChange=epoch
						continue
				### PERTURBATION ###
				print 'pert'
				Y=randomSubset(Ca.OB, Ca.ob)
				gMax=-os.sys.maxint-1
				Cm=None
				xMax=None
				for x in Y:
					for Cb in klusters:
						if Cb == Ca:
							continue
						if x in Cb.points:
							g=gain(Ca, Cb, x)
							if g > gMax:
								gMax=g
								Cm=Cb
								xMax=x
				if gMax > 0:
					print 'PERTURBATION, %d' % (epoch)
					Ca.add(xMax)
					Cm.rem(xMax)
					lastChange=epoch
		print 'last run at %d' % (epoch)
		#return klusters
		for cluster in klusters:
			if not cluster.isVoid():
				self.prototypes.add(cluster.mean)
		print 'prototypes', len(self.prototypes)
	
	def nsc(self):
		"""Nearest subclass classifier"""
		for p in self.universe:
			relative_distances=list()
			for proto in self.prototypes:
				relative_distances.append((distance(p, proto), proto.klasse))
			p.klasse=min(relative_distances)[1]
			self.classified.add(p)

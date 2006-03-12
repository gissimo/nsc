"""hard and dirty work for NSC implementation"""


import os, sys
import getopt
import Gnuplot
import math
import random
import nsc


def abstract_file(ifile_name, separator, klasse_index=None):
	"""reads punkts from file and returns them in a set"""
	intelligible=set()
	dim=0
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
			intelligible.add(nsc.punkt([float(i) for i in line], klasse))
		except ValueError:
			print 'WARNING: unable to understand line: %s' % (line)
			continue
	sfile.close()
	if len(intelligible) == 0:
		print '\nno values can be read from %s!\n' % (ifile_name)
		sys.exit()
	nsc.dim=dim
	return frozenset(intelligible)


def fill_world(sample):
	"""fills the nsc.welt dictionary with the points from the set sample"""
	for p in sample:
		if not nsc.welt.has_key(p.klasse):
			nsc.welt.setdefault(p.klasse, set())
		nsc.welt[p.klasse].add(p)


#def random_samples(to_sample, n):
#	"""computes a list of n random subsets of to_sample"""
#	#n=math.floor(math.sqrt(len(to_sample))).__int__()
#	#n=10
#	step=len(to_sample)/n
#	#print len(to_sample)
#	lamb=list(to_sample)
#	#print len(lamb)
#	#random.SystemRandom.shuffle(random.SystemRandom(os.urandom(4)), lamb)
#	lamb.reverse()
#	#print 'lamb', len(lamb)
#	#random.shuffle(lamb)
#	testing_sets=[None]*n
#	for i in xrange(n-1):
#		#testing_sets.insert(i, set())
#		#testing_sets[i].update(lamb[i:i+step])
#		testing_sets[i]=frozenset(lamb[i:i+step])
#	testing_sets[n-1]=frozenset(lamb[(n-1)*step:])
#	return testing_sets


#def random_samples(to_sample, n):
#	"""computes a list of n random subsets of to_sample"""
#	dimension=len(to_sample)/n
#	testing_sets=[None]*n
#	lamb=set(to_sample)
#	for i in xrange(n-1):
#		#print dimension
#		temp=frozenset(random.sample(lamb, dimension))
#		#temp=set(random.SystemRandom.sample(random.SystemRandom(os.urandom(4)), lamb, dimension))
#		#print len(temp)
#		testing_sets[i]=temp
#		#lamb.difference_update(temp)
#		lamb=lamb-temp
#		#print len(lamb)
#	testing_sets[n-1]=frozenset(lamb)
#	return testing_sets


def random_samples(to_sample, n):
	"""computes a list of n random subsets of to_sample"""
	testing_sets=[None]*n
	td={}
	for p in to_sample:
		if not td.has_key(p.klasse):
			td.setdefault(p.klasse, list([set(), None]))
		td[p.klasse][0].add(p)
	
	for k in td.keys():
		td[k][1]=len(td[k][0])/n
		#print 'rsk', len(td[k][0]), td[k][1], k
	
	for i in xrange(n-1):
		testing_sets[i]=set()
		for k in td.keys():
			rsk=random.sample(td[k][0], td[k][1])
			testing_sets[i].update(rsk)
			td[k][0].difference_update(rsk)
	testing_sets[n-1]=set()
	for k in td.keys():
		testing_sets[n-1].update(td[k][0])
	return testing_sets


def handle_commands(argv, short, long):
	try:
		opts, args=getopt.gnu_getopt(argv[1:], short, long)
	except getopt.error:
		usage(argv[0], short)
		sys.exit()
	
	ifile_name=None
	sigma=None
	pfile_name=None
	draws=None
	separator=None
	klasse_index=0
	
	if len(args) == 1:
		ifile_name=args[0]
	else:
		usage(argv[0], short)
		sys.exit()
	
	for opt, arg in opts:
		if opt == '-s':
			try:
				sigma=float(arg)
			except ValueError:
				usage(argv[0], short)
				print '\n-s requires a number'
				sys.exit()
		elif opt == '-p':
			pfile_name=arg
		elif opt == '-d':
			try:
				draws=int(arg)
			except ValueError:
				usage(argv[0], short)
				print '\n-d requires an integer'
				sys.exit()
		elif opt == '--separator':
			separator=arg
		elif opt == '--classid':
			try:
				klasse_index=int(arg)
			except ValueError:
				usage(argv[0], short)
				print '\n--classid requires an integer'
				sys.exit()

	if short.find('s') != -1 and (sigma == None or sigma < 0):
		usage(argv[0], short)
		print '\nsigma has to be greater or equal to zero'
		sys.exit()
	
	if short.find('d') != -1 and (draws == None or draws < 1):
		usage(argv[0], short)
		print '\nat least one draw'
		sys.exit()
	
	return ifile_name, sigma, pfile_name, draws, separator, klasse_index


def usage(argv0, short):
	s=p=''
	if short.find('s') != -1:
		s='-s variance costraint '
	if short.find('p') != -1:
		p='-p prototypes file '
	if short.find('d') != -1:
		d='-d draws '
	print '\nusage: %s filename %s%s%s[--separator char] [--classid 0|-1]' % (argv0.split(os.sep)[-1], s, p, d)


def statistics(array):
	total=0
	sqsum=0
	lower=100
	higher=0
	n=len(array)
	for i in array:
		total+=i
		sqsum+=i**2
		lower=min(lower, i)
		higher=max(higher, i)
	avg=total.__float__()/n
	stddev=math.sqrt(sqsum.__float__()/n - avg**2)
	return lower, avg, higher, stddev


#gestire visualizzazione con gnuplot
#usare eccezioni se non si puo' importare gnuplot

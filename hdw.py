"""hard and dirty work for NSC implementation"""


import os, sys
import getopt
import Gnuplot
import math
import random


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

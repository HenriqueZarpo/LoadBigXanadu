import csv
import time
import datetime
from time import mktime
import argparse
import shutil

#
#  2015-11-06 : v1.0 : Correction of bug in Flash.dump() that caused the program to raise an Error when len(flash.architecture) > nb products in architecture
#


mNew={}
nNew={}
aNew={}
iNew={}
oNew={}
pnNew={}
cNew={}
model={}
lifeCycles={}
oldFlash=None
newFlash=None
offersToPut=[]
isPacote=False
verbose = 1
modelPath=""
architecturePath=""
inPath=""
outPath=""
namesId={} # dictionary keeping for each name the corresponding ID. Easier like this rather than keeping track of the IDs during 
# the process

parser = argparse.ArgumentParser()
parser.add_argument('--category', "-c", type=str)
parser.add_argument('--architecture', "-a", type=str)
parser.add_argument('--model', "-m", type=str)
parser.add_argument('--i', "-i", type=str)
parser.add_argument('--out', "-o", type=str)
parser.add_argument('--verbose', "-v", type=int)

args = parser.parse_args()



class CategoryError(Exception):
	def __init__(self, message):
		 # Call the base class constructor with the parameters it needs
		 # Now for your custom code...
		 print message

# Color class for terminal output
class bcolors:
	PURPLE = '\033[1;95m'
	BLUE = '\033[1;94m'
	GREEN = '\033[1;32m'
	YELLOW = '\033[1;93m'
	RED = '\033[1;91m'
	purple = '\033[95m'
	blue = '\033[94m'
	green = '\033[32m'
	yellow = '\033[93m'
	red = '\033[91m'
	ENDC = '\033[0m'


	
class Size:
	BIG="B"
	SMALL="S"


class LifeCycle:
	def __init__(self):
		self.positions=[]
	def addPosition(self, time, position, size):
		self.positions.append((time, position, size))
		

#################################
#
# Builing custom category class
#
#################################

def buildFlashLifeCycle(self):
	
	global lifeCycles
	#
	# LifeCycles of Potentials
	#
	
	lcp3 = LifeCycle()
	lcp2 = LifeCycle()
	lcp1 = LifeCycle()
	lcp3.addPosition(2, 1, Size.BIG)
	lcp2.addPosition(2, 1, Size.SMALL)
	lcp1.addPosition(2, 2, Size.BIG)
	
	#
	# LifeCycles of Apoio
	#
	
	lca3 = LifeCycle()
	lca2 = LifeCycle()
	lca1 = LifeCycle()
	
	lca3.addPosition(2, 1, Size.BIG)
	lca3.addPosition(2, 1, Size.SMALL)
	lca3.addPosition(2, 2, Size.BIG)
	
	lca2.addPosition(2, 1, Size.SMALL)
	lca2.addPosition(2, 2, Size.BIG)
	
	lca1.addPosition(2, 1, Size.SMALL) # Really ?
	
	#
	# LifeCycles of Imagem
	#
	
	lci3 = LifeCycle()
	lci2 = LifeCycle()
	lci1 = LifeCycle()
	
	
	lci3.addPosition(3, 1, Size.BIG)
	lci3.addPosition(2, 2, Size.BIG)
	lci3.addPosition(2, 3, Size.BIG)
	
	lci2.addPosition(1, 1, Size.BIG)
	lci2.addPosition(2, 2, Size.BIG)
	lci2.addPosition(2, 3, Size.BIG)
	
	lci1.addPosition(2, 2, Size.BIG)
	lci1.addPosition(2, 3, Size.BIG)
	
	
	#
	# LifeCycles of Other
	#
	
	lco = LifeCycle()
	lco.addPosition(2, 2, Size.SMALL)
	
	lifeCycles={"P":[lcp1, lcp2, lcp3],
				"A":[lca1, lca2, lca3],
				"I":[lci1, lci2, lci3],
				"O":[lco]
				}

def buildPacoteLifeCycle(self):
	global lifeCycles
	lifeCycles={}


class CategoryMeta(type):
	"""
	This metaclass automagically converts ``buildLifeCycle`` method into
	static method
	"""
	#~ def __new__(cls, name, bases, d):
		#~ if 'buildLifeCycle' in d:
			#~ d['buildLifeCycle'] = make_analysator(d['buildLifeCycle'])
		#~ return type.__new__(cls, name, bases, d)
		
	def __new__(cls, name, bases, d):
		return type.__new__(cls, name, bases, d)


if args.category is None:
	if verbose >= 1:
		print "No category specified, assuming flash"
	Category = CategoryMeta('Category', (), {"MODEL": "M", "NEW": "P", "PUSH": "A", 
	"IMAGE": "I", "OTHER": "O","CRUISE": "C", "PN": "PN", "buildLifeCycle": buildFlashLifeCycle})

elif args.category == "flash" or args.category == "Flash":
	if verbose >= 2:
		print "Using category flash"
	Category = CategoryMeta('Category', (), {"MODEL": "M", "NEW": "P", "PUSH": "A", 
	"IMAGE": "I", "OTHER": "O", "buildLifeCycle": buildFlashLifeCycle})
	
elif args.category == "pacote" or args.category == "Pacote":
	isPacote=True
	if verbose >= 2:
		print "Using category pacote"
	Category = CategoryMeta('Category', (), {"MODEL": "M", "NEW": "P", "PUSH": "A", 
	"CRUISE": "C", "PN": "PN", "IMAGE": "I", "OTHER": "O", "buildLifeCycle": buildPacoteLifeCycle})
	
if isPacote:
	if args.verbose is not None:
		verbose = args.verbose
	
	if args.architecture is not None:
		architecturePath = args.architecture
	else:
		architecturePath = "architecturepacote.csv"
		
	if args.model is not None:
		modelPath = args.model
	else:
		modelPath = "modelpacote.csv"
		
	if args.i is not None:
		inPath = args.i
	else:
		inPath="pacote.csv"
		
	if args.out is not None:
		outPath = args.out
	else:
		outPath="sortedpacote.csv"
else:
	if args.verbose is not None:
		verbose = args.verbose
	
	if args.architecture is not None:
		architecturePath = args.architecture
	else:
		architecturePath = "architecture.csv"
		
	if args.model is not None:
		modelPath = args.model
	else:
		modelPath = "model.csv"
		
	if args.i is not None:
		inPath = args.i
	else:
		inPath="flash.csv"
		
	if args.out is not None:
		outPath = args.out
	else:
		outPath="sortedflash.csv"

if args.verbose is not None:
	verbose = args.verbose

#~ def makeCategories():
	#~ global categories
	#~ categories = [attr for attr in dir(Category()) if not callable(attr) and not attr.startswith("__")]
#~ 
#~ makeCategories()

#---------------------------------------------------------
#
#			Definition of the class Product
#
#---------------------------------------------------------
	
class Product:
	def __init__(self, i, n, p, c):
		self.priority = p
		self.name = n
		self.category=c
		self.key=i
		self.priorityM = None # this is the priority given by the model, not the one in the csv
		self.row=None
		self.index=None
		self.size=None
		self.date=None
	
	def setPosition(self, r, i, s): # Attention, la position est liee au produit et non a la flash !
		self.row=r
		self.index=i
		self.size=s
	
	def setDate(self, d):
		self.date=d
	
	# Deep copy of a product to avoid pointer related issues
	def copy(self):
		p = Product(self.key, self.name, self.priority, self.category)
		p.priorityM = self.priorityM
		p.row=self.row
		p.key=self.key
		p.index=self.index
		p.size=self.size
		p.date=self.date
		return p
		
	def __str__(self):
		p = self
		d=None
		if p.date is not None:
			d = time.strftime("%Y/%m/%d", p.date)
		return "{0} {1} {2} {3} {4}{5} {6} {7}".format(p.name, str(p.row), str(p.index), str(p.size), p.category, str(p.priority), str(p.priorityM), d)		
	
	def __repr__(self):
		p=self
		d = time.strftime("%Y/%m/%d", p.date)
		print "{0:40} \t{1} {2} {3} {4}{5} {6} {7}".format(p.name, str(p.row), str(p.index), str(p.size), p.category, str(p.priority), str(p.priorityM), d)		
		return ""
		
	def isIn(self):
		return self.row is not None
	
	def __cmp__(self, other):
		if verbose >= 3:
			print "compare " + str(self.name) + " and " + str(other.name)
		if self.category == Category.MODEL:
			if self.priorityM is None:
				return -1
			elif other.priorityM is None:
				return 1
			if verbose >= 3:
				print "result " + str(self.priorityM - other.priorityM)
			if self.priorityM != other.priorityM:
				return (self.priorityM - other.priorityM)/abs(self.priorityM - other.priorityM)
			else:
				return -1
		else:
			if self.priority == other.priority:
				if self.priorityM is None:
					return -1
				elif other.priorityM is None:
					return 1
				else:
					if self.priorityM != other.priorityM:
						return (self.priorityM - other.priorityM)/abs(self.priorityM - other.priorityM)
					else:
						return -1
			else:
				return (self.priority - other.priority)/abs(self.priority - other.priority)

	def isBefore(self, p2):
		return (self.row <= p2.row) or (self.row == p2.row and self.index <= p2.index)
		
	# Returns the position at which the product should be according to the lifecycle. Returns None if has finished the cycle
	def getPositionFromLifeCycle(self):
		try:
			lc = lifeCycles[self.category][self.priority-1]
			curPosInCycle=0
			now = datetime.datetime.now()
			delta = now - datetime.datetime.fromtimestamp(mktime(self.date))
			time=0
			for t in lc.positions:
				time+=t[0]
				if delta.days < time:
					if verbose >=1:		
						print "position in cycle for {0} is {1} (has been here for {2} days".format(self, curPosInCycle, delta.days)
					return curPosInCycle
				curPosInCycle+=1
			# at this stage the offer has stayed more than predicted by the lifecyle, the model ranking has to take over
			#which is done in Flash.insertItem
			return None
		except KeyError:
			if verbose >= 2:
				print "no life cycle defined for " + str(self) + " using defined architecture"
			return -1
					
	
# deprecated method
def getKey(p):
	return p.priorityM
	
	
#---------------------------------------------------------
#
#			Definition of the class Flash
#
#---------------------------------------------------------
	
class Flash:
	architecture=[]
	
	def __init__(self, prod):
		self.products=prod
	
			
	@staticmethod	
	def printArchitecture():
		r=0
		s=Size.BIG
		for p in Flash.architecture:
			if p.row > r:
				r = p.row
				print bcolors.blue+"\n\nrange " + str(r) + "\n" + bcolors.ENDC
			if p.size != s:
				s = p.size
				print "\n"
			print str(p.category) + " ",
		print "\n"
			
	
	
	def getModelPriorities(self):
		for p in self.products:
			try:
				findPriorityFromModel(p)
			except ValueError, e:
				print bcolors.RED + str(e) + bcolors.ENDC
			if verbose >= 2:
				print "Priority for {0} with category {2} is {1}".format(p.name, p.priorityM, p.category)
		
	
	# A better name should be found because though it can theorically sort anything it is only used for the model for the time
	# being	
	def sortByAndInsert(self, c):
		mods=[]
		for p in mNew.itervalues():
			mods.append(p)
		mods=sorted(mods,reverse=True)
		self.insertModel(mods, c)
	
	
	
	# returns the offer at the last position
	def getLast(self):
		tmp = self.architecture[0]
		for p in self.architecture:
			if p.row is not None:
				if tmp.isBefore(p):
					tmp = p
		return tmp
	
	# Apply the model for p according to its category. Returns None if lifecycle is finished and removes the product from
	# the corresponding list, or returns the position dictated by the model. WARNING: no index is defined by the model, 
	# it is necessary to check for every available position for this category at the given row and size
	def applyModel(self, p):
		plifecycle = p.getPositionFromLifeCycle()
		if plifecycle is None: # The offer has spent its time and the model ranking takes over
			print p,
			print bcolors.blue+" has finished its lifecycle, model takes over"+bcolors.ENDC
			if p.category == Category.PUSH: #do not delete because will change size of iterating list but mark as model
				#del aNew[p.name]
				pass
			elif p.category == Category.IMAGE:
				#del iNew[p.name]
				pass
			elif p.category == Category.OTHER:
				#del oNew[p.name]
				pass
			p.category = Category.MODEL
			mNew[p.key] = p
			return None
		elif plifecycle == -1: # no lifecycle defined for this one, happens for pacote for example
			p.setPosition(0, 0, p.size)
			firstP = self.findNextPosition(p)
			return (firstP.row, firstP.size)
		else:
			t = lifeCycles[p.category][p.priority-1]
			(d, r, s) = t.positions[plifecycle]
			if verbose >= 1:
				print p,
				print " should be at position " + str((r,s))
			return (r, s)
	
	# return the product at a given position
	def findProductAtPosition(self, r, s, i):
		for p in self.architecture:
			if p.row==r and p.size==s and p.index==i:
				return p
		# if no product was found, raise exception because the position has to be valid
		raise KeyError("Nothing was found in the architecture at the position {0} {1} {2}".format(r, s, i))
	
	# find next position for a given category according to the architecture. This position can be already occupied, 
	# the conflict gestion is done somechere else, but a new row is created if necessary. It either returns the product 
	# at this position in the currentArchitcture, or the product in the architecture with the added row
	def findNextPosition(self, pp):
		if verbose >= 1:
			print "finding next position for product " + str(pp)
		r = pp.row
		s = pp.size
		i = pp.index
		c = pp.category
		
		for p in self.architecture:
			if (p.row > r or (p.row==r and s==Size.BIG and p.size==Size.SMALL) or (p.row==r and s==p.size and p.index > i)) and p.category==c:
				if verbose >= 1:
					print " next position for product " + str(pp) + " is {0} {1} {2}".format(p.row, p.size, p.index)
				return p
		if verbose >= 1:
			print "no next position existing, we have to create some"
		last=p
		newP = Product(last.key, None, None, c)
		newP.setDate(p.date)
		# at this point no position was found, we have to either append to existing row or create a row						
		if last.size == Size.BIG and last.index < 4:
			if verbose >= 1:
				print "adding at the end of row {0} at index {1} with size {2}".format(last.row, last.index+1, last.size)
			newP.setPosition(last.row, last.index+1, last.size)
		elif last.size==Size.BIG and last.index >= 4:
			if verbose >= 1:
				print "No more space in row {0} at index {1} for Size big, adding in size Small".format(last.row, last.index+1)
			newP.setPosition(last.row, 0, Size.SMALL)
		elif last.size == Size.SMALL and last.index < 6:
			if verbose >= 1:
				print "adding at the end of row {0} at index {1} with size {2}".format(last.row, last.index+1, last.size)
			newP.setPosition(last.row, last.index+1, last.size)
		elif last.size == Size.SMALL and last.index >= 6:
			if verbose >= 1:
				print "No more space in row {0} adding a new row".format(last.row)
			newP.setPosition(last.row+1, 1, Size.BIG)
			
		# Adding the new position to the architecture
		self.architecture.append(newP)
		return newP
		
	def applyCustomRuleP3(self, p3):
		# testing if free image space in first range big
		i=-1
		for p in self.architecture:
			if p.row==1 and p.size==Size.BIG and p.name is None and p.category==Category.PUSH:
				i = p.index
				if verbose>=1:
					print "taking the apoio space at index {0} for custom P3 rule".format(i)
				break
		if i==-1:
			if verbose>=1:
				print "No free apoio space found at row 1 BIG, trying with Apoios"
		else:
			p=self.findProductAtPosition(1, Size.BIG, i)
			if verbose>=1:
				print bcolors.green+"Custom rule P3 was successful, inserting at index {0}\n".format(i)+bcolors.ENDC
			p.name=p3.name
			p.priority=p3.priority
			p.date=p3.date
			p.category=Category.NEW
			p.priorityM=p3.priorityM
			return True
			
		for p in self.architecture:
			if p.row==1 and p.size==Size.BIG and p.name is None and p.category==Category.IMAGE:
				i = p.index
				if verbose>=1:
					print "taking the image space at index {0} for custom P3 rule".format(i)
				break
		if i==-1:
			if verbose>=1:
				print "No free image space found at row 1 BIG either"
			return False
		else:
			p=self.findProductAtPosition(1, Size.BIG, i)
			if verbose>=1:
				print bcolors.green+"Custom rule P3 was successful, inserting at index {0}\n".format(i)+bcolors.ENDC
			p.name=p3.name
			p.priority=p3.priority
			p.date=p3.date
			p.category=Category.NEW
			p.priorityM=p3.priorityM
			p.key=p3.key
			return True
			
			
	# Insert a product in the architecture, relocating the conflicting objects. The calls to findNextPosition handle the 
	# creation of rows. 
	def insertProduct(self, p, r, s, i):
		if verbose >=1:
			print "trying to insert product " + str(p) + " at position {0} {1} {2}".format(r, s, i)
		
		# check if position conflicts with already placed product
		pthere = self.findProductAtPosition(r, s, i)
		if pthere.category != p.category:
			raise ValueError("Position to insert at is inconsistent with category")
		if pthere.name is not None: # there is a conflict
			if verbose >= 1:
				print bcolors.yellow+"conflict detected at position {0} {1} {2} between ".format(r, s, i) + str(p) + " and " + str(pthere) + bcolors.ENDC
			
			if p.category == Category.NEW and p.priority == 3 and not isPacote:
				if verbose>=1:
					print bcolors.YELLOW + "conflicts concerns two P3 products, applying custom rule..." + bcolors.ENDC
				if self.applyCustomRuleP3(p):
					return
				else:
					print bcolors.red + "haven't been able to apply the custom rule P3 for {0}, applying normal rule..." + bcolors.ENDC
			
			nextP = self.findNextPosition(pthere)
			
			# first we compare priorities
			
			if p.priority > pthere.priority:
				if verbose >= 1:
					print "{0} has higher priority, {1} is relocated".format(p, pthere)
				pcopy=pthere.copy()				
				pthere.name = p.name
				pthere.priority = p.priority
				pthere.priorityM = p.priorityM
				pthere.date = p.date
				pthere.key=p.key				
				self.insertProduct(pcopy, nextP.row, nextP.size, nextP.index)
				return
			elif p.priority < pthere.priority:
				if verbose >= 1:
					print "{0} has higher priority, {1} will be put somewhere else".format(pthere, p)
				self.insertProduct(p, nextP.row, nextP.size, nextP.index)
				return
				
			# Now at this stage the priorities are the same we check the dates 
			
			if p.date > pthere.date:
				if verbose >= 1:
					print "{0} is more recent, {1} is relocated".format(p, pthere)
				# we relocate a copy because the next steps overwrite pthere (pointer)
				pcopy=pthere.copy()				
				pthere.name = p.name
				pthere.priority = p.priority
				pthere.priorityM = p.priorityM
				pthere.date = p.date
				pthere.key=p.key				
				self.insertProduct(pcopy, nextP.row, nextP.size, nextP.index)
				return
			elif p.date < pthere.date:
				if verbose >= 1:
					print "{0} is more recent, {1} will be put somewhere else".format(pthere, p)
				self.insertProduct(p, nextP.row, nextP.size, nextP.index)
				return
			
			# Now at this stage the priorities and the dates are the same, we compare with the model
			else:
				if p.__cmp__(pthere) == -1: # p is lower than pthere in the model
					if verbose >= 1:
						print "{0} is higher in the model, {1} will be put somewhere else".format(pthere, p)
					self.insertProduct(p, nextP.row, nextP.size, nextP.index)
					return
				else:
					if verbose >= 1:
						print "{0} is higher in the model, {1} is relocated".format(p, pthere)
					# we relocate a copy because the next steps overwrite pthere (pointer)
					pcopy=pthere.copy()				
					pthere.name = p.name
					pthere.priority = p.priority
					pthere.priorityM = p.priorityM
					pthere.date = p.date				
					self.insertProduct(pcopy, nextP.row, nextP.size, nextP.index)
					return
			# if we still haven't returned there is a bug
			raise ValueError("Unable to perform insertion")
		else: #pthere.name is none we can safely insert
			if verbose >=1:
				print bcolors.green+ "Inserting product " + str(p) + " at position {0} {1} {2}\n".format(r, s, i) +bcolors.ENDC
			pthere.name = p.name
			pthere.priority = p.priority
			pthere.priorityM = p.priorityM
			pthere.date = p.date
			pthere.key=p.key
					
	
	# find all the available index for a certain category at row r and size s			
	def findAvailableIndexesForCatAt(self, c, r, s):
		idxs = []
		for p in self.architecture:
			if (p.row == r and p.size == s and p.category == c):
				idxs.append(p.index)
		if len(idxs) == 0:
			raise ValueError("No available index at position {0} {1} for category {2}".format(r, s, c))
		return idxs
		
	# Iterates through the dictionary corresponding to a category and isert its elements
	def insertCategory(self, cat):
		if verbose >= 1:
			print "\n\n Inserting category " + str(cat) + "\n"
		l = None
		if cat == Category.NEW:
			l=nNew
		elif cat == Category.IMAGE:
			l=iNew
		elif cat == Category.PUSH:
			l=aNew
		elif cat == Category.OTHER:
			l=oNew
		elif cat == Category.PN:
			l=pnNew
		elif cat == Category.CRUISE:
			l=cNew
		for p in l.itervalues():
			t = self.applyModel(p)	
			if t is None: #offer has expired
				pass
			else:
				(r, s) = (t[0], t[1])
				idxs = self.findAvailableIndexesForCatAt(cat, r, s)
				if len(idxs) == 1: # there is no ambiguity we can check for conflict at this position
					i = idxs[0]
					self.insertProduct(p, r, s, i)
				else: 
					# there are a different available indexes but we can safely take the first one
					# because the "findNextAvailable position will take care of going trough these indexes
					# in case of conflict
					i = idxs[0]
					self.insertProduct(p, r, s, i)
					
					
	# insert the sorted model at all empty positions
	def insertModel(self, mods, cat):
		k=0
		last=None
		if verbose >= 2:
			print bcolors.BLUE + "printing the result of the sort" + bcolors.ENDC
			for p in mods:
				print p
		for p in self.architecture:
			if k == len(mods):
				return
			if p.name is None: # this is an empty position
				r=mods[k]
				p.name=r.name
				p.date=r.date 
				p.priorityM=r.priorityM
				p.category=r.category
				p.key=r.key
				k+=1
		last = self.getLast()
		if verbose >= 2:	
			print "k is "+ str(k) + " while len mods is " + str(len(mods))
			print last
		while k < len(mods): # It is possible to reduce the number of cases but it is clearer like this
			if verbose >= 2:	
				print last
			if last.size == Size.BIG and last.index < 5:
				if verbose >= 1:
					print "adding at the end of row {0} at index {1} with size {2}".format(last.row, last.index+1, last.size)
				p=mods[k]
				p.setPosition(last.row, last.index+1, last.size)
				self.architecture.append(p)
				last=p
				k+=1
			elif last.size==Size.BIG and last.index>=5:
				if verbose >= 1:
					print "No more space in row {0} at index {1} for Size big, adding in size Small".format(last.row, last.index+1)
				p=mods[k]
				p.setPosition(last.row, 0, Size.SMALL)
				self.architecture.append(p)
				last=p
				k+=1
			elif last.size == Size.SMALL and last.index < 6:
				if verbose >= 1:
					print "adding at the end of row {0} at index {1} with size {2}".format(last.row, last.index+1, last.size)
				p=mods[k]
				p.setPosition(last.row, last.index+1, last.size)
				self.architecture.append(p)
				last=p
				k+=1
			elif last.size == Size.SMALL and last.index >= 6: # Hack for now, because new architecture with 8 small at the end breaks it
				if verbose >= 1:
					print "No more space in row {0} adding a new row".format(last.row)
				p=mods[k]
				p.setPosition(last.row+1, 1, Size.BIG)
				self.architecture.append(p)
				last=p
				k+=1	
					

	def __repr__(self):
		r=0
		for p in self.architecture:
			if p.row > r:
				print "\n"
				r = p.row
			if p.row is None:
				print bcolors.purple
			print p
			if p.row is None:
				print bcolors.ENDC
		return ""
		
	def dump(self):
		with open(outPath, "wb+") as csvfile:
			writer = csv.writer(csvfile, delimiter=',', quotechar='"')
			row=["Name", "Row", "Index", "Size", "Category", "Priority", "Date", "Configurable product Id"]
			writer.writerow(row)
			for p in self.architecture:
				if p.name!=None:
					row[0] = p.name
					row[1] = p.row
					row[2] = p.index
					row[3] = p.size
					row[4] = p.category
					row[5] = p.priority
					d = time.strftime("%Y/%m/%d", p.date)
					row[6] = d
					row[7] = namesId[p.name]
					writer.writerow(row)
			#~ print "writing others"
			#~ for p in oNew.itervalues():
				#~ row[0] = p.name
				#~ row[1] = ""
				#~ row[2] = ""
				#~ row[3] = ""
				#~ row[4] = p.category
				#~ row[5] = p.priority
				#~ d = time.strftime("%Y/%m/%d", p.date)
				#~ row[6] = d
				#~ writer.writerow(row)



def readOffersToPut():
	for p in offersToPut:
		try:
			n = p.key
			if p.category == "M":
				try:
					mNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					mNew[n] = p
			elif p.category == "P":
				try:
					nNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					nNew[n] = p
			elif p.category == "A":
				try:
					aNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					aNew[n] = p
			elif p.category == "I":
				try:
					iNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					iNew[n] = p
			elif p.category == "O":
				try:
					oNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					oNew[n] = p
			elif p.category == "PN":
				try:
					pnNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					pnNew[n] = p
			elif p.category == "C":
				try:
					cNew[n]
					raise ValueError("dois produtos com mismo SKU")
				except KeyError:
					cNew[n] = p
		except ValueError,e:
			print str(e)
	if verbose >= 1:
		print "\n\nProdutos cargados: \n"
		for value in mNew.itervalues():
			print "Melhores produtos: " + value.name
		for key, value in nNew.iteritems():
			print "Potencial: " + value.name + " com prioridade: " + str(value.priority)
		for key, value in aNew.iteritems():
			print "Apoios: " + value.name + " com prioridade: " + str(value.priority)
		for key, value in iNew.iteritems():
			print "Imagem: " + value.name + " com prioridade: " + str(value.priority)
		for key, value in pnNew.iteritems():
			print "Pacote national: " + value.name + " com prioridade: " + str(value.priority)
		for key, value in cNew.iteritems():
			print "Cruzeiros: " + value.name + " com prioridade: " + str(value.priority)
		print "\n\n"



def readModel():
	with open(modelPath, "rU") as csvfile:
		reader = csv.reader(csvfile, delimiter=",",dialect=csv.excel_tab)
		for row in reader:
			print row
			if row[0] == "": # for excel newline
				break
			p = Product(int(row[2]),row[0].strip(), None, Category.MODEL)
			p.priorityM = float(row[1])
			try:
				model[p.key]
				raise ValueError("dois produtos tem o mismo nome no modelo")
			except KeyError:
				model[p.key] = p
	if verbose >= 3:
		print model

# Finds the priority given by the model to a product
def findPriorityFromModel(p):
	try:
		x = model[p.key]
		p.priorityM = x.priorityM
	except KeyError:
		if p.category != Category.NEW:
			print bcolors.RED + "O produto {0} com categoria {1} e sku {2} nao foi encontrado no modelo".format(p.name, p.category, p.key) + bcolors.ENDC
	
# Parses the flash csv on the following model:	
# name cat prior isHighlight date isNew id
def readFormerFlash():
	global oldFlash
	global offersToPut
	with open(inPath, "rU") as csvfile:
		shutil.copy(inPath, "./archive/"+datetime.datetime.now().strftime("%Y%m%d")+inPath)
		reader = csv.reader(csvfile, delimiter=",")
		tmp=[]
		rg=1
		idx=1
		sz=Size.BIG;
		for row in reader:
			try:
				c=None
				# A changer pour qqch de plus general
				row[1]=row[1].strip()
				if row[1] == Category.MODEL:
					c=Category.MODEL
				elif row[1] == Category.NEW:
					c=Category.NEW
				elif row[1] == Category.PUSH:
					c=Category.PUSH
				elif row[1] == Category.IMAGE:
					c=Category.IMAGE
				elif row[1] == Category.OTHER:
					c=Category.OTHER
				elif row[1] == "":
					c=Category.MODEL #default
				elif row[1] == Category.PN:
					c=Category.PN
				elif row[1] == Category.CRUISE:
					c=Category.CRUISE
				else:
					raise CategoryError("Unrecognized category: " + row[1])
				key = int(row[6])
				namesId[row[0]]=key
				if c == Category.OTHER or c == Category.MODEL or c == Category.PN or c == Category.CRUISE:
					p = Product(key, row[0].strip(), 1, c)
				else:	
					p = Product(key, row[0].strip(), int(row[2]), c)
				if row[5] == "0":
					#~ if row[3] == "1" and sz==Size.BIG:
						#~ p.setPosition(rg, idx, Size.BIG)
						#~ idx+=1
					#~ elif row[3] == "1" and sz==Size.SMALL: # We went to the next range
						#~ rg+=1
						#~ idx=1
						#~ sz=Size.BIG
						#~ p.setPosition(rg, idx, Size.BIG)
						#~ idx+=1
					#~ elif row[3] == "0" and sz==Size.BIG:
						#~ idx=1
						#~ sz=Size.SMALL
						#~ p.setPosition(rg, idx, Size.SMALL)
						#~ idx+=1
					#~ elif row[3] == "0" and sz==Size.SMALL:
						#~ p.setPosition(rg, idx, Size.SMALL)
						#~ idx+=1
					#~ else:
						#~ print "error in row " + str(row)
					
					if row[4] == "":
						if verbose >=1:
							print "no date found at row " + str(row) + " using today's date"
						p.setDate(time.strptime(time.strftime("%Y/%m/%d"), "%Y/%m/%d"))
					else:
						p.setDate(time.strptime(row[4], "%Y/%m/%d"))
					tmp.append(p)
					offersToPut.append(p)
				else:
					if verbose >=1:
						print "new offer to put with category " + p.category
					p.setDate(time.strptime(time.strftime("%Y/%m/%d"), "%Y/%m/%d"))
					offersToPut.append(p)
			except (ValueError, AttributeError, CategoryError), e:
				if type(e) == ValueError or CategoryError:
					print bcolors.RED+str(e) + " " + str(row) + bcolors.ENDC
		oldFlash = Flash(tmp)
		#oldFlash.getModelPriorities()
		if verbose >= 3:
			print oldFlash

# read the architecture which is fully customizable			
def readArchitecture():
	with open(architecturePath, "rU") as csvfile:
		reader = csv.reader(csvfile, delimiter=",")
		tmp=[]
		rg=1
		idx=1
		sz=Size.BIG;
		for row in reader:
			try:
				c=None
				try:
					if row[0] == Category.MODEL:
						c=Category.MODEL
					elif row[0] == Category.NEW:
						c=Category.NEW
					elif row[0] == Category.PUSH:
						c=Category.PUSH
					elif row[0] == Category.IMAGE:
						c=Category.IMAGE
					elif row[0] == Category.OTHER:
						c=Category.OTHER
					elif row[0] == "":
						c=Category.MODEL #default
					elif row[0] == Category.PN:
						c=Category.PN
					elif row[0] == Category.CRUISE:
						c=Category.CRUISE
					else:
						raise CategoryError("Unrecognized category: " + row[1])
				except AttributeError:
					pass
				p = Product(None, None, None, c)
				if row[1] == "1" and sz==Size.BIG:
					p.setPosition(rg, idx, Size.BIG)
					idx+=1
				elif row[1] == "1" and sz==Size.SMALL: # We went to the next range
					rg+=1
					idx=1
					sz=Size.BIG
					p.setPosition(rg, idx, Size.BIG)
					idx+=1
				elif row[1] == "0" and sz==Size.BIG:
					idx=1
					sz=Size.SMALL
					p.setPosition(rg, idx, Size.SMALL)
					idx+=1
				elif row[1] == "0" and sz==Size.SMALL:
					p.setPosition(rg, idx, Size.SMALL)
					idx+=1
				else:
					print "error in row " + str(row)
			except ValueError, e:
				print bcolors.RED+str(e) + " " + str(row) + bcolors.ENDC
			tmp.append(p)
		Flash.architecture=tmp
		
Category().buildLifeCycle() # build the life cycle according to the given rules
readModel()	
readArchitecture()
Flash.printArchitecture()
readFormerFlash()
readOffersToPut()
newFlash=Flash(offersToPut)
newFlash.getModelPriorities() # retrieves the priorities given by the model for every offer
if not isPacote:
	newFlash.insertCategory(Category.PUSH)
	newFlash.insertCategory(Category.IMAGE)
	newFlash.insertCategory(Category.NEW) # it is important to inster NEW after the two others for the custom rule P3
	newFlash.insertCategory(Category.OTHER)
else:
	newFlash.insertCategory(Category.PUSH)
	newFlash.insertCategory(Category.PN)
	newFlash.insertCategory(Category.CRUISE)
	newFlash.insertCategory(Category.NEW)
	
newFlash.sortByAndInsert(Category.MODEL)
newFlash.dump()


if verbose >= 1:
	print newFlash	
				

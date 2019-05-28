import math
import operator
import random

from deap import gp

def protectedDiv(left, right):
	try:
		return left /right
	except ZeroDivisionError:
		return 1

pset = gp.PrimitiveSet("MAIN", arity=1)
pset.renameArguments(ARG0='x')

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 1)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(math.sin, 1)
pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))


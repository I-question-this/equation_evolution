#!/usr/bin/env python3
"""
"""
import math
import operator
import random
from deap import gp

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

# Protected operators
def protectedDiv(left, right):
  try:
    return left / right
  except ZeroDivisionError:
    return 1

def protectedPow(base, exponent):
  if base == 0:
    return 0
  result = base**exponent
  return result.real if type(result) == complex else result

def createPrimitiveSet():
  pset = gp.PrimitiveSet("MAIN", arity=1)
  pset.renameArguments(ARG0='x')

  pset.addPrimitive(operator.add, 2)
  pset.addPrimitive(operator.sub, 2)
  pset.addPrimitive(operator.mul, 2)
  pset.addPrimitive(protectedDiv, 2, name="div")
  pset.addPrimitive(protectedPow, 2, name="pow")
  pset.addPrimitive(operator.neg, 1)
  pset.addPrimitive(math.cos, 1)
  pset.addPrimitive(math.sin, 1)
  pset.addEphemeralConstant("rand", lambda: random.randint(-1,1))

  return pset

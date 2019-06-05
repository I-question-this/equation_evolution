#!/usr/bin/env python3
"""
"""
import operator
from deap import gp

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

def toolboxRegistration(mutationSubTreeHeightMin, mutationSubTreeHeightMax, maxTreeHeight, pset, toolbox):
  toolbox.register("mate", gp.cxOnePoint)
  toolbox.register("expr_mut", gp.genFull, min_=mutationSubTreeHeightMin, max_=mutationSubTreeHeightMax)
  toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

  toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=maxTreeHeight))
  toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=maxTreeHeight))

  return toolbox


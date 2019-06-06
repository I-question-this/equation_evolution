#!/usr/bin/env python3
"""
"""
import numpy
from .framework import evaluation
from .framework import mutation
from .framework import population
from .framework import primitives
from .framework import stats
from deap import base
from deap import tools

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

# Parameters
benignWeight = -1.0
malwareWeight = -100.0
benignEquation = "add(pow(x,add(1,1)),add(1,1))"
malwareEquation = "add(pow(x,add(1,add(1,1))),add(1,add(1,add(1,1)))"
malwareStartX = 0
malwareEndX = 1
mutationSubTreeHeightMin = 0
mutationSubTreeHieghtMax = 2
maxTreeHeight = 17

def createToolbox(testPoints):
  pset = primitives.createPrimitiveSet()

  toolbox = base.Toolbox()

  individGen = population.individualGenerator(benignWeight, malwareWeight, pset)
  toolbox = population.toolboxRegistration(individGen, benignEquation, malwareEquation, pset, toolbox)

  toolbox = mutation.toolboxRegistration(mutationSubTreeHeightMin, mutationSubTreeHieghtMax, maxTreeHeight, pset, toolbox)

  toolbox = evaluation.toolboxRegistration(malwareStartX, malwareEndX, pset, toolbox)
#  toolbox = evaluation.registerEvaluationThroughSymbolicRegression(testPoints, toolbox)
  toolbox = evaluation.registerEvaluationThroughIntegration(min(testPoints), max(testPoints), toolbox)

  toolbox = stats.toolboxRegistration(toolbox)

  return toolbox

def replaceInfiniteErrorIndividuals(replacementSelection):
  def decorator(func):
    def wrapper(*args, **kargs):
      valids = [ind for ind in args[0] if not numpy.isinf(ind.fitness.values[0]) and not numpy.isinf(ind.fitness.values[1])]
      for ind, index in zip(args[0], range(len(args[0]))):
        if numpy.isinf(ind.fitness.values[0]) or numpy.isinf(ind.fitness.values[1]):
          args[0][index] = replacementSelection(valids, 1)[0]
      return func(*args, **kargs)
    return wrapper
  return decorator
        

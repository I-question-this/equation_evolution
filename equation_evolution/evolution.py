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


def createToolbox(name, benignEquation, fitnessWeight, malwareEquation, malwareStartX, malwareStopX, maxTreeHeight, mutationSubTreeHeightMax, mutationSubTreeHeightMin, testPoints):
  pset = primitives.createPrimitiveSet(name)

  toolbox = base.Toolbox()

  individGen = population.individualGenerator(name, fitnessWeight, pset)
  toolbox = population.toolboxRegistration(individGen, benignEquation, malwareEquation, pset, toolbox)

  toolbox = mutation.toolboxRegistration(mutationSubTreeHeightMin, mutationSubTreeHeightMax, maxTreeHeight, pset, toolbox)

  toolbox = evaluation.toolboxRegistration(malwareStartX, malwareStopX, pset, toolbox)

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
        

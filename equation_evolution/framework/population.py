#!/usr/bin/env python3
"""
"""
import random
from deap import base
from deap import creator
from deap import gp
from deap import tools

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

def individualGenerator(benignWeight, malwareWeight, pset):
  creator.create("TrojanFitnessMin", base.Fitness, weights=(benignWeight, malwareWeight))
  creator.create("Individual", gp.PrimitiveTree, fitness=creator.TrojanFitnessMin, pset=pset)
  return creator.Individual

def toolboxRegistration(individualGenerator, benignEquation, malwareEquation, pset, toolbox):
  toolbox.register("manualEquation", gp.PrimitiveTree.from_string, pset=pset)
  toolbox.register("benignEquation", lambda equ: equ, equ=toolbox.manualEquation(benignEquation))
  toolbox.register("malwareEquation", lambda equ: equ, equ=toolbox.manualEquation(malwareEquation))
  toolbox.register("randomEquation", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)

  def starterEquation():
    rand = random.random()
    if rand < 0.333333:
      return toolbox.randomEquation()
    elif rand < 0.666666:
      return toolbox.benignEquation()
    else:
      return toolbox.malwareEquation()

  toolbox.register("starterEquation", starterEquation)
  toolbox.register("individual", tools.initIterate, individualGenerator, toolbox.starterEquation)
  toolbox.register("population", tools.initRepeat, list, toolbox.individual)

  return toolbox


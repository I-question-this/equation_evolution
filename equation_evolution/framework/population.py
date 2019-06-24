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

def individualGenerator(name, weight, pset):
  creator.create("{}FitnessMin".format(name), base.Fitness, weights=(weight,))
  creator.create("{}Individual".format(name), gp.PrimitiveTree, fitness=getattr(creator, "{}FitnessMin".format(name)), pset=pset)
  return getattr(creator, "{}Individual".format(name))

def toolboxRegistration(individualGenerator, benignEquation, malwareEquation, pset, toolbox):
  toolbox.register("manualEquation", gp.PrimitiveTree.from_string, pset=pset)
  toolbox.register("randomEquation", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
  if benignEquation is None:
    benignEquation = str(individualGenerator(gp.genFull(pset, 5, 10)))
  toolbox.register("benignEquation", lambda equ: equ, equ=toolbox.manualEquation(benignEquation))
  if malwareEquation is None:
    malwareEquation = str(individualGenerator(gp.genFull(pset, 5, 10)))
  toolbox.register("malwareEquation", lambda equ: equ, equ=toolbox.manualEquation(malwareEquation))

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


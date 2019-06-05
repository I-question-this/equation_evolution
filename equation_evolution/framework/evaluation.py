#!/usr/bin/env python3
"""
"""
import math
import matplotlib.pyplot as plt
import numpy
import operator
import pygraphviz as pgv
import random
from deap import base
from deap import creator
from deap import gp
from deap import tools
from scipy import integrate
from scipy.optimize import fsolve

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

def evalSymbReg(individual, points, toolbox):
  # Transform the tree expression in a callable function
  func = toolbox.compile(expr=individual)
  # Evaluate the mean squared errors
  def calculateError(x, equation):
    try:
      return (func(x) - equation(x))**2
    except OverflowError:
      return numpy.inf

  benignErrors = []
  malwareErrors = []
  for x in points:
    if toolbox.inMalwareRange(x):
      malwareErrors.append(calculateError(x, lambda x: toolbox.compiledMalwareEquation(x)))
    else:
      benignErrors.append(calculateError(x, lambda x: toolbox.compiledBenignEquation(x)))

  return math.fsum(benignErrors) / len(benignErrors), math.fsum(malwareErrors) / len(malwareErrors)

def areaBetweenTwoFunctions(func1, func2, lowerLimit, upperLimit):
  """The abs is to handle intersecting lines. From what I understand this is mathimatically valid.
  """
  return integrate.quad(lambda x: abs(func1(x)-func2(x)), lowerLimit, upperLimit)

def evalIntegration(individual, lowerLimit, upperLimit, toolbox):
  # Transform the tree expression in a callable function
  func = toolbox.compile(expr=individual)
  # Return the area between the target functions
  try:
    benignError = areaBetweenTwoFunctions(func, toolbox.benignEquation, lowerLimit, malware_xMin)[0]
    benignError += areaBetweenTwoFunctions(func, toolbox.benignEquation, malware_xMax, upperLimit)[0]
    malwareError = areaBetweenTwoFunctions(func, toolbox.malwareEquation, malware_xMin, malware_xMax)[0]
    return benignError, malwareError
  except OverflowError:
    return numpy.inf, numpy.inf

def toolboxRegistration(malwareStartX, malwareEndX, pset, toolbox):
  toolbox.register("compile", gp.compile, pset=pset)
	
  toolbox.register("compiledBenignEquation", lambda x, eqn: eqn(x), eqn=toolbox.compile(toolbox.benignEquation()))
  toolbox.register("compiledMalwareEquation", lambda x, eqn: eqn(x), eqn=toolbox.compile(toolbox.malwareEquation()))
  toolbox.register("inMalwareRange", lambda x: malwareStartX <= x <= malwareEndX)
  toolbox.register("pieceWiseFunction", lambda x: toolbox.compiledMalwareEquation(x) if toolbox.inMalwareRange(x) else toolbox.compiledBenignEquation(x))


  toolbox.register("evalSymbReg", evalSymbReg, toolbox=toolbox)
  toolbox.register("evalIntegration", evalIntegration, toolbox=toolbox)

  return toolbox

def registerEvaluationThroughSymbolicRegression(points, toolbox):
  toolbox.register("evaluate", toolbox.evalSymbReg, points=points)
  return toolbox

def registerEvaluationThroughIntegration(lowerLimit, upperLimit, toolbox):
  toolbox.register("evaluate", toolbox.evalIntegration, lowerLimit=lowerLimit, upperLimit=upperLimit)
  return toolbox

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
    except (OverflowError, ValueError) as e:
      print("func({}): {} | equation({}): {}".format(x, func(x), x, equation(x)))
      return numpy.inf

  errors = []
  for x in points:
    errors.append(calculateError(x, toolbox.pieceWiseFunction))

  return math.fsum(errors) / len(errors),

def areaBetweenTwoFunctions(func1, func2, lowerLimit, upperLimit):
  """The abs is to handle intersecting lines. From what I understand this is mathimatically valid.
  """
  return integrate.quad(lambda x: abs(func1(x)-func2(x)), lowerLimit, upperLimit)[0]

def evalIntegration(individual, lowerLimit, upperLimit, malwareStartX, malwareEndX, toolbox):
  # Transform the tree expression in a callable function
  func = toolbox.compile(expr=individual)
  # Return the area between the target functions
  """
  try:
    if malwareStartX <= lowerLimit:
      benignError = areaBetweenTwoFunctions(func, toolbox.compiledBenignEquation, malwareEndX, upperLimit)
    elif malwareEndX >= upperLimit:
      benignError = areaBetweenTwoFunctions(func, toolbox.compiledBenignEquation, lowerLimit, malwareStartX)
    else:
      benignError = areaBetweenTwoFunctions(func, toolbox.compiledBenignEquation, lowerLimit, malwareStartX) + areaBetweenTwoFunctions(func, toolbox.compiledBenignEquation, malwareEndX, upperLimit)
  except OverflowError:
    benignError = numpy.inf

  try:
    malwareError = areaBetweenTwoFunctions(func, toolbox.compiledMalwareEquation, max(lowerLimit,malwareStartX), min(upperLimit,malwareEndX))
  except OverflowError:
    malwareError = numpy.inf
  """
  error = areaBetweenTwoFunctions(func, toolbox.pieceWiseFunction, lowerLimit, upperLimit) 

  return error, error

def toolboxRegistration(malwareStartX, malwareEndX, pset, toolbox):
  toolbox.register("compile", gp.compile, pset=pset)
	
  toolbox.register("compiledBenignEquation", lambda x, eqn: eqn(x), eqn=toolbox.compile(toolbox.benignEquation()))
  toolbox.register("compiledMalwareEquation", lambda x, eqn: eqn(x), eqn=toolbox.compile(toolbox.malwareEquation()))
  toolbox.register("inMalwareRange", lambda x: malwareStartX <= x <= malwareEndX)
  toolbox.register("pieceWiseFunction", lambda x: toolbox.compiledMalwareEquation(x) if toolbox.inMalwareRange(x) else toolbox.compiledBenignEquation(x))


  toolbox.register("evalSymbReg", evalSymbReg, toolbox=toolbox)
  toolbox.register("evalIntegration", evalIntegration,malwareStartX=malwareStartX, malwareEndX=malwareEndX, toolbox=toolbox)

  return toolbox

def registerEvaluationThroughSymbolicRegression(points, toolbox):
  toolbox.register("evaluate", toolbox.evalSymbReg, points=points)
  return toolbox

def registerEvaluationThroughIntegration(lowerLimit, upperLimit, toolbox):
  toolbox.register("evaluate", toolbox.evalIntegration, lowerLimit=lowerLimit, upperLimit=upperLimit)
  return toolbox


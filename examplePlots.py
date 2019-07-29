#!/usr/bin/env python3
"""Output methods
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import pygraphviz as pgv
from deap import creator, gp
from equation_evolution.output import plotEquationStructure
from equation_evolution.primitives import pset
from equation_evolution.setup import creatorSetup
from functools import partial

creatorSetup(-2.0)

outputDirectory = "presentationOutput"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)
outputPath = partial(os.path.join, outputDirectory)

class EquationInformation:
  def __init__(self, formal, primitive):
    self.formal = formal
    self.primitive = primitive
    self.tree = gp.PrimitiveTree.from_string(self.primitive, pset=pset)
    self.compiled = gp.compile(self.tree, pset=pset)

def plotLinearRegression(line1Function, line1Name, line1Color, line2Function, line2Name, points, outputName, insertionStart=None, insertionStop=None):
    # Plot the lines
    plt.plot(points, [line1Function(x) for x in points], line1Color,
        label=line1Name
    )
    plt.plot(points, [line2Function(x) for x in points], 'g--',
        label=line2Name
    )

    # Mark the linear regression
    label="Linear Regression"
    for point in points:
      plt.plot([point, point], [line1Function(point), line2Function(point)], 'c', label=label)
      label=None

    # Mark the insertion start and stop points
    if insertionStart is not None and insertionStop is not None:
      plt.axvline(insertionStart, label="Inseration start/stop")
      plt.axvline(insertionStop)

    # Make the legend
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2,
        mode="expand", borderaxespad=0.
    )
    # Save the figure
    plt.savefig(outputName)
    # Close the figure
    plt.close()

if __name__ == "__main__":
  equation1 = EquationInformation("x + 1", "add(x,1)")
  equation2 = EquationInformation("x + 2", "add(x,add(1,1))")
  #evoTrojanEquation = EquationInformation("JESUS", "add(sub(x, neg(pow(1.0, x))), cos(mul(sin(x), x)))")
  evoTrojanEquation = EquationInformation("JESUS", "add(sub(add(x, cos(0.0)), mul(sub(add(sin(sin(0.0)), mul(x, pow(add(x, 1.0), pow(div(mul(neg(cos(sub(x, x))), 0.0), 0.0), cos(div(1.0, -1.0)))))), sin(div(x, cos(x)))), div(sub(cos(neg(sub(0.0, 0.0))), pow(add(cos(x), neg(-1.0)), -1.0)), x))), div(cos(x), pow(pow(sin(1.0), pow(mul(x, pow(cos(mul(x, x)), cos(cos(add(0.0, sub(sin(mul(-1.0, mul(0.0, 1.0))), add(x, -1.0))))))), div(mul(sin(x), mul(0.0, x)), cos(div(x, 0.0))))), add(cos(cos(add(add(x, neg(sin(pow(mul(add(add(sin(x), cos(add(cos(x), mul(x, x)))), x), mul(sin(x), x)), x)))), x))), div(div(div(mul(cos(0.0), sub(cos(sub(0.0, cos(add(x, sin(mul(1.0, x)))))), div(add(cos(sub(cos(x), cos(sin(div(1.0, x))))), cos(x)), sin(neg(x))))), x), pow(x, mul(add(sub(mul(add(sin(x), add(sin(div(x, x)), add(mul(pow(x, mul(x, x)), div(x, x)), 1.0))), pow(sub(x, sub(0.0, x)), mul(sub(x, cos(mul(x, x))), add(pow(x, sub(pow(x, 0.0), mul(-1.0, x))), neg(mul(-1.0, sub(1.0, 0.0))))))), div(div(add(cos(x), sub(1.0, x)), cos(cos(neg(0.0)))), sub(sub(x, cos(1.0)), mul(x, x)))), cos(div(x, -1.0))), sub(neg(neg(add(x, sin(-1.0)))), cos(x))))), x)))))")

  plotEquationStructure(equation1.tree, outputPath("x_plus_1.png"))
  plotEquationStructure(equation2.tree, outputPath("x_plus_2.png"))
  plotEquationStructure(evoTrojanEquation.tree, outputPath("evoTrojanFinal.png"))

  points = np.arange(-2,2.25,0.25)
  plotLinearRegression(equation1.compiled, "Benign", "b--", equation2.compiled, "Malware", points, outputPath("linearRegressionExample_Malware_Benign.png"))
  insertionStart = -1.0
  insertionStop = 1.0
  def trojanFunction(x):
    if insertionStart <= x <= insertionStop:
      return equation2.compiled(x)
    else:
      return equation1.compiled(x)

  plotLinearRegression(equation1.compiled, "Evolved Trojan Gen. 0 / Benign", "r--", trojanFunction, "Ideal Piecewise Trojan", points, outputPath("linearRegressionExample_IdealPieceWiseTrojan_Benign.png"),
    insertionStart, insertionStop)

  plotLinearRegression(evoTrojanEquation.compiled, "Evolved Trojan Final", "r--", trojanFunction, "Ideal Piecewise Trojan", points, outputPath("linearRegressionExample_IdealPieceWiseTrojan_EvoTrojanFinal.png"),
    insertionStart, insertionStop)


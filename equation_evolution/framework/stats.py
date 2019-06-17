#!/usr/bin/env python3
"""
"""
import matplotlib.pyplot as plt
import numpy
import pygraphviz as pgv
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

def plotEquationStructure(individual, output_name):
  nodes, edges, labels = gp.graph(individual)

  g = pgv.AGraph()
  g.add_nodes_from(nodes)
  g.add_edges_from(edges)
  g.layout(prog="dot")

  for i in nodes:
    n = g.get_node(i)
    n.attr["label"] = labels[i]

  g.draw(output_name)


def plotEquationResults(individual, points, output_name, toolbox):
  func = toolbox.compile(expr=individual)

  plt.plot(points, [func(x) for x in points], 'r', label="Evolved Trojan")
  plt.plot(points, [toolbox.pieceWiseFunction(x) for x in points], 'b--', label="Piecewise Target")
  plt.plot(points, [toolbox.compiledMalwareEquation(x) for x in points], 'g--', label="Malware")
  plt.plot(points, [toolbox.compiledBenignEquation(x) for x in points], 'k--', label="Benign")
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
  plt.savefig(output_name)

def toolboxRegistration(toolbox):
  toolbox.register("plotEquationResults", plotEquationResults, toolbox=toolbox)
  toolbox.register("plotEquationStructure", plotEquationStructure)

  return toolbox

def createStatisticsObject():
  stats_benign = tools.Statistics(lambda ind: ind.fitness.values[0])
  stats_malware = tools.Statistics(lambda ind: ind.fitness.values[1])
  stats_size = tools.Statistics(len)

  mstats = tools.MultiStatistics(benign=stats_benign, malware=stats_malware, size=stats_size)
  mstats.register("avg", numpy.mean)
  mstats.register("std", numpy.std)
  mstats.register("min", numpy.min)
  mstats.register("max", numpy.max)

  return mstats


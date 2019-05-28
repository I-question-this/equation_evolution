#!/usr/bin/env python3
"""Defines what and how is being evolved using DEAP.
The important exports of this file are toolbox (contains
evolutionary process) and mstats (contains methods used
for collecting statistics on the evolutionary process).
"""
import math
import numpy
import operator
import pygraphviz as pgv
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

# Primatives
def protectedDiv(left, right):
	try:
		return left /right
	except ZeroDivisionError:
		return 1

pset = gp.PrimitiveSet("MAIN", arity=1)
pset.renameArguments(ARG0='x')

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 2)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(math.sin, 1)
pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))

# Creator
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin,
               pset=pset)

# Tool registration
toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual,
                 toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def evalSymbReg(individual, points):
	# Transform the tree expression in a collable function
	func = toolbox.compile(expr=individual)
	# Evaluate the mean squared error between the expression
	# and the real function: x**4 - x**3 + x**2 + x
	sqerrors = ((func(x) - x**4 - x**3 - x**2 - x)**2 for x in points)
	return math.fsum(sqerrors) / len(points),

toolbox.register("evaluate", evalSymbReg, points=[x/10. for x in range(-10,10)])
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

def plotGraph(individual, output_name):
	nodes, edges, labels = gp.graph(individual)

	g = pgv.AGraph()
	g.add_nodes_from(nodes)
	g.layout(prog="dot")

	for i in nodes:
		n = g.get_node(i)
		n.attr["label"] = labels[i]

	g.draw(output_name)

toolbox.register("graph", plotGraph)

# Statistics
stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
stats_size = tools.Statistics(len)
mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
mstats.register("avg", numpy.mean)
mstats.register("std", numpy.std)
mstats.register("min", numpy.min)
mstats.register("max", numpy.max)

if __name__ == "__main__":
	# No tests currently defined for this file
	pass


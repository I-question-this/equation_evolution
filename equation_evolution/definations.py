#!/usr/bin/env python3
"""Defines what and how is being evolved using DEAP.
The important exports of this file are toolbox (contains
evolutionary process) and mstats (contains methods used
for collecting statistics on the evolutionary process).
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

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

def createEnvironment(benign_equation, malware_equation, malware_xMin, malware_xMax):
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
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=pset)

	# Tool registration
	toolbox = base.Toolbox()
	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)
	toolbox.register("manualExpr", gp.PrimitiveTree.from_string, pset=pset)

	def pieceWiseFunction(x, benign_equation, malware_equation, malware_xMin, malware_xMax):
		if malware_xMin <= x <= malware_xMax:
			return malware_equation(x)
		else:
			return benign_equation(x)
	toolbox.register("pieceWiseFunction", pieceWiseFunction, benign_equation=toolbox.compile(toolbox.manualExpr(benign_equation)), malware_equation=toolbox.compile(toolbox.manualExpr(malware_equation)), malware_xMin=malware_xMin, malware_xMax=malware_xMax)

	def evalSymbReg(individual, points):
		# Transform the tree expression in a collable function
		func = toolbox.compile(expr=individual)
		# Evaluate the mean squared error between the expression
		# and the real function: x**4 - x**3 + x**2 + x
		sqerrors = ((func(x) - toolbox.pieceWiseFunction(x))**2 for x in points)
		return math.fsum(sqerrors) / len(points),

	toolbox.register("evaluate", evalSymbReg, points=[x/10. for x in range(-100,100)])
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("mate", gp.cxOnePoint)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

	toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

	def plotEquationStructure(individual, output_name):
		nodes, edges, labels = gp.graph(individual)

		g = pgv.AGraph()
		g.add_nodes_from(nodes)
		g.layout(prog="dot")

		for i in nodes:
			n = g.get_node(i)
			n.attr["label"] = labels[i]

		g.draw(output_name)

	toolbox.register("plotEquationStructure", plotEquationStructure)

	def plotEquationResults(individual, output_name):
		Xs = [x/10. for x in range(-100,100)] # -10->10 with .1 steps
		func = toolbox.compile(expr=individual)

		plt.plot(Xs, [func(x) for x in Xs], 'r', label="Evolved Trojan")
		plt.plot(Xs, [toolbox.pieceWiseFunction(x) for x in Xs], 'b', label="Piecewise Target")
		plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
		plt.savefig(output_name)
	
	toolbox.register("plotEquationResults", plotEquationResults)


	# Statistics
	stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
	stats_size = tools.Statistics(len)
	mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
	mstats.register("avg", numpy.mean)
	mstats.register("std", numpy.std)
	mstats.register("min", numpy.min)
	mstats.register("max", numpy.max)

	return toolbox, mstats

if __name__ == "__main__":
	# No tests currently defined for this file
	pass


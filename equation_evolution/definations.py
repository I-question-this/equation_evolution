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
			return left / right
		except ZeroDivisionError:
			return 1

	def protectedPow(base, exponent):
		if base == 0:
			return 0
		result = base**exponent
		return result.real if type(result) == complex else result

	pset = gp.PrimitiveSet("MAIN", arity=1)
	pset.renameArguments(ARG0='x')

	pset.addPrimitive(operator.add, 2)
	pset.addPrimitive(operator.sub, 2)
	pset.addPrimitive(operator.mul, 2)
	pset.addPrimitive(protectedDiv, 2, name="div")
	pset.addPrimitive(protectedPow, 2, name="pow")
	pset.addPrimitive(operator.neg, 1)
	pset.addPrimitive(math.cos, 1)
	pset.addPrimitive(math.sin, 1)
	pset.addEphemeralConstant("rand", lambda: random.randint(-1,1))

	# Creator
	creator.create("FitnessMin", base.Fitness, weights=(-1.0, -100.0))
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=pset)

	# Tool registration
	toolbox = base.Toolbox()
	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)
	toolbox.register("manualExpr", gp.PrimitiveTree.from_string, pset=pset)
	
	toolbox.register("benignEquation", lambda x, eqn: eqn(x), eqn=toolbox.compile(toolbox.manualExpr(benign_equation)))
	toolbox.register("malwareEquation", lambda x, eqn: eqn(x), eqn=toolbox.compile(toolbox.manualExpr(malware_equation)))
	toolbox.register("inMalwareRange", lambda x, rangeMin, rangeMax: rangeMin <= x <= rangeMax, rangeMin=malware_xMin, rangeMax=malware_xMax)
	toolbox.register("pieceWiseFunction", lambda x: toolbox.malwareEquation(x) if toolbox.inMalwareRange(x) else toolbox.benignEquation(x))

	def evalSymbReg(individual, points):
		# Transform the tree expression in a collable function
		func = toolbox.compile(expr=individual)
		# Evaluate the mean squared errors
		benignErrors = []
		malwareErrors = []
		for x in points:
			if toolbox.inMalwareRange(x):
				malwareErrors.append((func(x) - toolbox.malwareEquation(x))**2)
			else:
				benignErrors.append((func(x) - toolbox.benignEquation(x))**2)

		return math.fsum(benignErrors) / len(benignErrors), math.fsum(malwareErrors) / len(malwareErrors)

	toolbox.register("evaluate", evalSymbReg, points=[x/10. for x in range(-20,20)])
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
		Xs = [x/10. for x in range(-20,20)]
		func = toolbox.compile(expr=individual)

		plt.plot(Xs, [func(x) for x in Xs], 'r', label="Evolved Trojan")
		plt.plot(Xs, [toolbox.pieceWiseFunction(x) for x in Xs], 'b--', label="Piecewise Target")
		plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
		plt.savefig(output_name)
	
	toolbox.register("plotEquationResults", plotEquationResults)


	# Statistics
	stats_benign = tools.Statistics(lambda ind: ind.fitness.values[0])
	stats_malware = tools.Statistics(lambda ind: ind.fitness.values[1])
	stats_size = tools.Statistics(len)
	mstats = tools.MultiStatistics(benign=stats_benign, malware=stats_malware, size=stats_size)
	mstats.register("avg", numpy.mean)
	mstats.register("std", numpy.std)
	mstats.register("min", numpy.min)
	mstats.register("max", numpy.max)

	return toolbox, mstats

if __name__ == "__main__":
	# No tests currently defined for this file
	pass


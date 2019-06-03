#!/usr/bin/env python3
"""Driver program for equation_evolution.
Using the toolbox and mstats defined equation_evolution.definations
the evolutionary process is run.
"""
from deap import algorithms
from deap import tools
from equation_evolution.definations import createEnvironment

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

def main(toolbox, mstats):
	pop = toolbox.population(n=100)
	hof = tools.HallOfFame(1)
	pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 500, stats=mstats, halloffame=hof, verbose=True)
	
	return pop, log, hof

if __name__ == "__main__":
	toolbox, mstats = createEnvironment("add(pow(x,add(1,1)),add(1,1))", "add(pow(x,add(1,add(1,1))),add(1,add(1,add(1,1)))", 0, 1)
	pop, log, hof = main(toolbox, mstats)
	print(log.stream)
	toolbox.plotEquationStructure(hof[0], "halloffame--equation_structure.png")
	toolbox.plotEquationResults(hof[0], "halloffame--equation_results.png")


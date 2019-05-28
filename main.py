#!/usr/bin/env python3
"""Driver program for equation_evolution.
Using the toolbox and mstats defined equation_evolution.definations
the evolutionary process is run.
"""
from deap import algorithms
from deap import tools
from equation_evolution.definations import toolbox, mstats

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

def main():
	pop = toolbox.population(n=30)
	hof = tools.HallOfFame(1)
	pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats=mstats, halloffame=hof, verbose=True)
	
	return pop, log, hof

if __name__ == "__main__":
	pop, log, hof = main()
	print(log.stream)
	toolbox.graph(hof[0], "halloffame.png")


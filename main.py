#!/usr/bin/env python3
"""Driver program for equation_evolution.
Using the toolbox and mstats defined equation_evolution.definations
the evolutionary process is run.
"""
from deap import algorithms
from deap import tools
from equation_evolution import evolution
from equation_evolution.framework import stats 

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"

if __name__ == "__main__":
  testPoints = [x/10. for x in range(-20,20)]

  toolbox = evolution.createToolbox(testPoints)
  toolbox.register("select", tools.selTournament, tournsize=3)
  def newIndividual(*args, **kargs):
    return [toolbox.individual()]
  toolbox.decorate("select", evolution.replaceInfiniteErrorIndividuals(newIndividual))

  pop = toolbox.population(n=100)
  mstats = stats.createStatisticsObject()
  hof = tools.HallOfFame(1)
 
  pop, log = algorithms.eaSimple(pop, toolbox, 0.1, 0.5, 200, stats=mstats, halloffame=hof)
  
  toolbox.plotEquationStructure(hof[0], "halloffame--equation_structure.png")
  toolbox.plotEquationResults(hof[0], testPoints, "halloffame--equation_results.png")


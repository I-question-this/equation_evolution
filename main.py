#!/usr/bin/env python3
"""Driver program for equation_evolution.
Using the toolbox and mstats defined equation_evolution.definations
the evolutionary process is run.
"""
import argparse
import numpy as np
from deap import algorithms
from deap import tools
from equation_evolution import evolution
from equation_evolution.framework import evaluation
from equation_evolution.framework import stats 

__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"


def processArguments(inputArgs=None):

  # Argument parsing
  parser = argparse.ArgumentParser()
  parser.add_argument("--benign_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  parser.add_argument("--crossover_probability", type=np.float_, default=0.1,
    help="The probability of cross over: 0<=x<=1"
  )
  parser.add_argument("--fitness_weight", type=lambda x: -(abs(np.float_(x))),
    default=-2.0, help="Since it's minimized error it is transformed into a negative"
  )
  parser.add_argument("--hall_of_fame_max_size", type=lambda x: abs(int(x)),
    default=1, help="Number of individuals to save in the hall of fame"
  )
  parser.add_argument("--malware_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  parser.add_argument("--malware_start_x", type=np.float_, default=-1.0,
    help="The value that the malware equation is started to be inserted into"
  )
  parser.add_argument("--malware_stop_x", type=np.float_, default=1.0,
    help="The value that the malware equation inseration stops at"
  )
  parser.add_argument("--max_tree_height", type=lambda x: abs(x), default=17,
    help="The maximum tree size of the equations"
  )
  parser.add_argument("--mutation_probability", type=np.float_, default=0.5,
    help="The probability of mutation: 0<=x<=1"
  )
  parser.add_argument("--mutation_sub_tree_max", type=int, default=2,
    help="The maximum size possible for the sub tree created in a mutation"
  ) 
  parser.add_argument("--mutation_sub_tree_min", type=int, default=0,
    help="The minimum size possible for the sub tree created in a mutation"
  ) 
  parser.add_argument("--number_of_generations", type=lambda x: abs(int(x)),
    default=1000, help="The number of generations for the evolutation"
  )
  parser.add_argument("--number_of_individuals", type=lambda x: abs(int(x)),
    default=50, help="The number of individuals in each generation"
  )
  parser.add_argument("--test_points_start", type=np.float_, default=-2,
    help="Start paramter for test points generated with numpy.arange"
  )
  parser.add_argument("--test_points_stop", type=np.float_, default=2.25,
    help="Stop paramter for test points generated with numpy.arange"
  )
  parser.add_argument("--test_points_step", type=np.float_, default=0.25,
    help="Step paramter for test points generated with numpy.arange"
  )

  return parser.parse_args(inputArgs)


def runEvolution(args, output_name):
  testPoints = np.array(np.arange(
    args.test_points_start,
    args.test_points_stop,
    args.test_points_step
  ))

  toolbox = evolution.createToolbox(
    output_name,
    args.benign_equation,
    args.fitness_weight,
    args.malware_equation,
    args.malware_start_x,
    args.malware_stop_x,
    args.max_tree_height,
    args.mutation_sub_tree_max,
    args.mutation_sub_tree_min,
    testPoints
  )

  toolbox = evaluation.registerEvaluationThroughSymbolicRegression(testPoints, toolbox)

  toolbox.register("select", tools.selTournament, tournsize=3)
  def newIndividual(*args, **kargs):
    return [toolbox.individual()]
#  toolbox.decorate("select", evolution.replaceInfiniteErrorIndividuals(newIndividual))

  pop = toolbox.population(n=args.number_of_individuals)
  mstats = stats.createStatisticsObject()
  hof = tools.HallOfFame(args.hall_of_fame_max_size)
 
  pop, log = algorithms.eaSimple(
    pop, 
    toolbox, 
    args.crossover_probability, 
    args.mutation_probability,
    args.number_of_generations,
    stats=mstats, 
    halloffame=hof
  )

  for individualN in range(len(hof)):  
    toolbox.plotEquationStructure(
      hof[individualN],
      "{}--halloffame-{}--equation_structure.png".format(
        output_name,
        individualN
      )
    )
    toolbox.plotEquationResults(
      hof[individualN],
      testPoints,
      "{}--halloffame-{}--equation_results.png".format(
        output_name,
        individualN
      )
    )
    toolbox.writeEquation(
      hof[individualN],
      "{}--halloffame-{}--equation_written.txt".format(
        output_name,
        individualN
      )
    )

  return hof


if __name__ == "__main__":
  args = processArguments()

  # Create the best trojan
  hof = runEvolution(args, "trojanCreation")

  trojanEquation = str(hof[0])

  # Setup for evolving out the trojan
  args.malware_equation = trojanEquation
  args.malware_start_x = args.test_points_stop
  args.malware_stop_x = args.test_points_stop

  runEvolution(args, "trojanRemoval")


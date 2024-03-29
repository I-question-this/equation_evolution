#!/usr/bin/env python3
"""Driver program for equation_evolution.
Using the toolbox and mstats defined equation_evolution.definations
the evolutionary process is run.
"""
import argparse
import matplotlib.pyplot as plt
import numpy as np
import operator
import os
import pickle
from deap import algorithms, base, creator, gp, tools
from equation_evolution.algorithm import evolveUntilCondition
from equation_evolution.setup import creatorSetup, toolboxDirectSetup, toolboxGaussianSetup
from equation_evolution.stats import mstats
from functools import partial
__author__ = "Tyler Westland"
__copyright__ = "Copyright 2019, Tyler Westland"
__credits__ = ["Tyler Westland"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer = "Tyler Westland"
__email__ = "westlatr@mail.uc.edu"
__status__ = "Prototype"


def _processArguments(inputArgs=None):

  # Argument parsing
  parser = argparse.ArgumentParser()
  parser.add_argument("benign_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  parser.add_argument("benign_equation_type", help="A descriptor of the type of equation")
  parser.add_argument("malware_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  parser.add_argument("malware_equation_type", help="A descriptor of the type of equation")
  parser.add_argument("--output_name", default="equationEvolution.pickle",
          help="Specifiy the output name"
  )
  parser.add_argument("--direct", action="store_true", default=False,
          help="Uses the direct manipluation of an equation instead of gausian"
  )
  parser.add_argument("--verbose", action='store_true', default=False, help="Rather to output results of each generation")
  parser.add_argument("--trojan_creation_target_error", type=np.float_, default=0.0,
          help="Minimum error required for the generation process to end early for creation. Default is 0.0"
  )
  parser.add_argument("--trojan_removal_target_error", type=np.float_, default=0.0,
          help="Minimum error required for the generation process to end early for removal. Default is 0.0"
  )
  parser.add_argument("--crossover_probability", type=np.float_, default=0.1,
    help="The probability of cross over: 0<=x<=1"
  )
  parser.add_argument("--fitness_weight", type=lambda x: -(abs(np.float_(x))),
    default=-2.0, help="Since it's minimized error it is transformed into a negative"
  )
  parser.add_argument("--insertion_start", type=np.float_, default=-1.0,
    help="The value that the malware equation is started to be inserted into"
  )
  parser.add_argument("--insertion_stop", type=np.float_, default=1.0,
    help="The value that the malware equation inseration stops at"
  )
  parser.add_argument("--max_tree_height", type=lambda x: abs(x), default=17,
    help="The maximum tree size of the equations"
  )
  parser.add_argument("--mutation_probability", type=np.float_, default=0.5,
    help="The probability of mutation: 0<=x<=1"
  )
  parser.add_argument("--mutation_sub_tree_height_max", type=int, default=2,
    help="The maximum size possible for the sub tree created in a mutation"
  ) 
  parser.add_argument("--mutation_sub_tree_height_min", type=int, default=0,
    help="The minimum size possible for the sub tree created in a mutation"
  ) 
  parser.add_argument("--max_number_of_generations", type=lambda x: abs(int(x)),
    default=1000, help="The maximum number of generations for the evolutation"
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
  parser.add_argument("--redoRemovalPickle",
    help="File path to a pickle to redo the removal without redoing the creation. Yes this option was made because a horrible bug was found in the removal process."
  )
  parser.add_argument("--special_removal", action="store_true", default=False,
    help="Evolves based on the size of the benign equation as well as the outputs"
  )


  return parser.parse_args(inputArgs)


def runEvolution(args, toolbox, targetError):
  # Run the evoluationary algorithm
  pop = toolbox.population(n=args.number_of_individuals)
  hof = tools.HallOfFame(1)

  # Define funcitons for stopping output
  def sufficientlyLowError(population, hallOfFame, error):
      return all(value <= error for value in hallOfFame[0].fitness.values)

  hof, pop, gen, logbook, rndstate = evolveUntilCondition(toolbox, pop, hof, args.mutation_probability, 
          args.crossover_probability, mstats,
          partial(sufficientlyLowError, error=targetError),
          args.max_number_of_generations, args.verbose)

  return {"hallOfFame": hof, "endingPopulation": pop, "generationsUsed": gen, 
          "maximumGenerationsAllowed": args.max_number_of_generations,
          "targetError": targetError, "logbook": logbook, "rndstate": rndstate
         }

if __name__ == "__main__":
  args = _processArguments()
  creatorSetup(args.fitness_weight, args.fitness_weight)
  if args.direct:
    toolbox = toolboxDirectSetup(args.benign_equation, args.malware_equation,
            args.mutation_sub_tree_height_min, args.mutation_sub_tree_height_max,
            args.max_tree_height, args.test_points_start, args.test_points_stop,
            args.test_points_step, args.insertion_start, args.insertion_stop
            )
  else:
    toolbox = toolboxGaussianSetup(args.benign_equation, args.malware_equation,args.mutation_sub_tree_height_min,
            args.mutation_sub_tree_height_max, args.max_tree_height, args.test_points_start, args.test_points_stop,
            args.test_points_step, args.insertion_start, args.insertion_stop, -3, 3
            )

  # Create the Trojan
  toolbox.register("evaluate", toolbox.evalSymbReg, targetFunction=toolbox.pieceWiseFunction)
  if args.redoRemovalPickle is None:
    creationResults = runEvolution(args, toolbox, args.trojan_creation_target_error)
  else:
    with open(args.redoRemovalPickle, "rb") as fileIn:
      previousResults = pickle.load(fileIn)
      creationResults = previousResults["creation"]

  # Remove the Trojan
  # Redefine individuals to start as the Trojan
  if args.direct:
    trojan = toolbox.manualEquation(str(creationResults["hallOfFame"][0]))
    toolbox.unregister("evaluate")
  else:
    trojan = toolbox.manualEquation(toolbox.guassianTrojanAsPrimitives(
              creationResults["hallOfFame"][0],
              toolbox.benignEquationPrimitiveTree
            ))
    toolbox = toolboxDirectSetup(args.benign_equation, args.malware_equation,
            args.mutation_sub_tree_height_min, args.mutation_sub_tree_height_max,
            args.max_tree_height, args.test_points_start, args.test_points_stop,
            args.test_points_step, args.insertion_start, args.insertion_stop
            )
  # Redefine the individual for removal
  toolbox.unregister("individual")
  toolbox.register("individual",
      tools.initIterate,
      creator.RemovalIndividual if args.special_removal else creator.DirectIndividual,
      lambda: trojan
  )
  # Redfine the population with the new individual
  toolbox.unregister("population")
  toolbox.register("population", tools.initRepeat, list,
    toolbox.individual
  )
  # Redefine the evaluation function
  def removalEvaluate(individual, targetFunction):
      symbRegFitness = toolbox.evalSymbReg(individual, targetFunction)[0]
      sizeFitness = abs(len(individual) - len(toolbox.benignEquationPrimitiveTree()))
      return symbRegFitness, sizeFitness

  toolbox.register("evaluate", removalEvaluate,
          targetFunction=toolbox.benignEquation
  )
  removalResults = runEvolution(args, toolbox, args.trojan_removal_target_error)

  # Save all the results
  results = {"creation": creationResults,
             "removal": removalResults,
             "testPoints": {
                 "start": args.test_points_start,
                 "stop": args.test_points_stop,
                 "step": args.test_points_step
             },
             "insertion": {
                 "start": args.insertion_start,
                 "stop": args.insertion_stop
             },
             "fitnessWeight": args.fitness_weight,
             "mutationSubTreeHeight": {
                 "min": args.mutation_sub_tree_height_min,
                 "max": args.mutation_sub_tree_height_max
             },
             "benignEquation": args.benign_equation,
             "benignEquationType": args.benign_equation_type,
             "malwareEquation": args.malware_equation,
             "malwareEquationType": args.malware_equation_type,
             "maxTreeHeight": args.max_tree_height,
             "version": 1.3
            }
  with open(args.output_name, "wb") as fStream:
    print("Saving results to '{}'".format(args.output_name))
    pickle.dump(results, fStream)


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
import pygraphviz as pgv
from deap import algorithms, base, creator, gp, tools
from equation_evolution.algorithm import evolveUntilCondition
from equation_evolution.primitives import pset
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
  parser.add_argument("malware_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  parser.add_argument("--output_name", default="equationEvolution.pickle",
          help="Specifiy the output name"
  )
  parser.add_argument("--verbose", action='store_true', default=False, help="Rather to output results of each generation")
  parser.add_argument("--trojan_creation_target_error", type=np.float_, default=0.05,
          help="Minimum error required for the generation process to end early for creation. Default is 0.05"
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
  parser.add_argument("--insertion_start_x", type=np.float_, default=-1.0,
    help="The value that the malware equation is started to be inserted into"
  )
  parser.add_argument("--insertion_stop_x", type=np.float_, default=1.0,
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

  return parser.parse_args(inputArgs)


def _setup(args):
  # Create an emtpy toolbox
  toolbox = base.Toolbox()
  
  # Create a custom type
  creator.create("FitnessMin", base.Fitness,
     weights=(args.fitness_weight,)
  )
  creator.create("Individual", gp.PrimitiveTree,
    fitness=creator.FitnessMin, pset=pset
  )


  # Define creation of the equations
  toolbox.register("manualEquation", gp.PrimitiveTree.from_string,
    pset=pset
  )
  benignEquationPrimitiveTree = toolbox.manualEquation(args.benign_equation)
  malwareEquationPrimitiveTree = toolbox.manualEquation(args.malware_equation)
  
  # Define creation of indiviuals for the  population
  toolbox.register("individual", tools.initIterate, creator.Individual, 
          lambda: benignEquationPrimitiveTree
  )
  toolbox.register("population", tools.initRepeat, list,
   toolbox.individual
  )

  # Define mutation properties
  toolbox.register("mate", gp.cxOnePoint)
  toolbox.register("expr_mut", gp.genFull,
     min_=args.mutation_sub_tree_height_min,
     max_=args.mutation_sub_tree_height_max
  )
  toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut,
    pset=pset
  )

  toolbox.decorate("mate",
    gp.staticLimit(key=operator.attrgetter("height"),
    max_value=args.max_tree_height)
  )
  toolbox.decorate("mutate",
    gp.staticLimit(key=operator.attrgetter("height"),
    max_value=args.max_tree_height)
  )

  # Define equation compiling
  toolbox.register("compile", gp.compile, pset=pset)

  # Create the array of points that will be used for test
  testPoints = np.array(np.arange(
    args.test_points_start,
    args.test_points_stop,
    args.test_points_step
  ))
  # Define evaluation
  def evalSymbReg(individual, targetFunction, points):
    # Transform the tree expression in a callable function
    equation = toolbox.compile(expr=individual)
    # Evaluate the mean squared errors

    errors = np.power(
               np.subtract(
                 np.fromiter(map(equation, points), np.float_),
                 np.fromiter(map(targetFunction, points),
                    np.float_
                 )
               ), 
               2
             )
    # Return average mean squared error
    return np.mean(errors),
  toolbox.register("evalSymbReg", evalSymbReg, points=testPoints)

  def pieceWiseFunction(x, benignEquation, malwareEquation, insertionStart, insertionStop):
    if insertionStart <= x <= insertionStop:
      return malwareEquation(x)
    else:
      return benignEquation(x)
  
  benignEquationCompiled = toolbox.compile(benignEquationPrimitiveTree)
  malwareEquationCompiled = toolbox.compile(malwareEquationPrimitiveTree)
  toolbox.register("pieceWiseFunction", pieceWiseFunction,
          benignEquation=benignEquationCompiled, malwareEquation=malwareEquationCompiled,
          insertionStart=args.insertion_start_x, insertionStop=args.insertion_stop_x
  )
 
  # Set selection method
  toolbox.register("select", tools.selTournament, tournsize=3)

  return toolbox


def runEvolution(args, toolbox, targetError):
  # Run the evoluationary algorithm
  pop = toolbox.population(n=args.number_of_individuals)
  hof = tools.HallOfFame(1)

  # Define funcitons for stopping output
  def sufficientlyLowError(population, hallOfFame, error):
      return hallOfFame[0].fitness.values[0] <= error

  hof, pop, gen = evolveUntilCondition(toolbox, pop, hof, args.mutation_probability, 
          args.crossover_probability, mstats,
          partial(sufficientlyLowError, error=targetError),
          args.max_number_of_generations, args.verbose)

  return {"hallOfFame": hof, "endingPopulation": pop, "generationsUsed": gen, 
          "maximumGenerationsAllowed": args.max_number_of_generations}

if __name__ == "__main__":
  args = _processArguments()
  toolbox = _setup(args)
  # Create the Trojan
  toolbox.register("evaluate", toolbox.evalSymbReg, targetFunction=toolbox.pieceWiseFunction)
  creationResults = runEvolution(args, toolbox, args.trojan_creation_target_error)
  # Remove the Trojan
  toolbox.unregister("evaluate")
  toolbox.register("evaluate", toolbox.evalSymbReg,
          targetFunction=toolbox.compile(creationResults["hallOfFame"][0])
  )
  removalResults = runEvolution(args, toolbox, args.trojan_removal_target_error)

  # Save all the results
  results = {"creation": creationResults, "removal": removalResults}
  with open(args.output_name, "wb") as fStream:
    print("Saving results to '{}'".format(args.output_name))
    pickle.dump(results, fStream)


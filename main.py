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
import pygraphviz as pgv
import random
from deap import algorithms, base, creator, gp, tools

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
  parser.add_argument("starting_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  parser.add_argument("target_equation",
    help="Can be any of the primitives and the parameter 'x'"
  )
  def trueOrFalse(string:str):
    if string.lower() == "true":
      return True
    if string.lower() == "false":
      return False
    raise ValueError("Must be 'True' or 'False'")

  parser.add_argument("trojan_creation", type=trueOrFalse,
    help="<True,False>: States rather we are creating or removing a trojan. Purely for labeling purposes in the produced plot."
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
  parser.add_argument("--target_start_x", type=np.float_, default=-1.0,
    help="The value that the malware equation is started to be inserted into"
  )
  parser.add_argument("--target_stop_x", type=np.float_, default=1.0,
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


def runEvolution(args):
  # Create an emtpy toolbox
  toolbox = base.Toolbox()

  # Create the primatives
  # Protected operators
  def protectedDiv(left, right):
    if right == 0:
      return 0
    else:
      return left / right

  def protectedPow(base, exponent):
    if base == 0:
      return 0

    result = np.power(base, exponent, dtype=np.float_)
    return 0 if np.isinf(result) or np.isnan(result) else result

  # Create the primative set
  pset = gp.PrimitiveSet("MainPset", arity=1)
  pset.renameArguments(ARG0='x')

  pset.addPrimitive(operator.add, 2)
  pset.addPrimitive(operator.sub, 2)
  pset.addPrimitive(operator.mul, 2)
  pset.addPrimitive(protectedDiv, 2, name="div")
  pset.addPrimitive(protectedPow, 2, name="pow")
  pset.addPrimitive(operator.neg, 1)
  pset.addPrimitive(np.cos, 1)
  pset.addPrimitive(np.sin, 1)
  pset.addEphemeralConstant("rand101",
     lambda: np.float_(random.randint(-1,1))
  )

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
  toolbox.register("startingEquation",
    lambda: toolbox.manualEquation(args.starting_equation)
  )
  toolbox.register("targetEquation",
     lambda: toolbox.manualEquation(args.target_equation) if args.target_equation is not None else None
  )

  # Define creation of indiviuals for the  population
  toolbox.register("individual", tools.initIterate, creator.Individual, 
    toolbox.startingEquation
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

  # Define evaluation of the population
  toolbox.register("compile", gp.compile, pset=pset)

  compiledStartingEquation = toolbox.compile(toolbox.startingEquation())
  if toolbox.targetEquation() is not None:
    compiledTargetEquation = toolbox.compile(toolbox.targetEquation())
  else:
    compiledTargetEquation = None

  def pieceWiseFunction(x):
    if args.target_start_x <= x <= args.target_stop_x and compiledTargetEquation is not None:
      return compiledTargetEquation(x)
    else:
      return compiledStartingEquation(x)


  def evalSymbReg(individual, points):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the mean squared errors

    errors = np.power(
               np.subtract(
                 np.fromiter(map(func, points), np.float_),
                 np.fromiter(map(pieceWiseFunction, points),
                    np.float_
                 )
               ), 
               2
             )
    # Return average mean squared error
    return np.mean(errors),

  testPoints = np.array(np.arange(
    args.test_points_start,
    args.test_points_stop,
    args.test_points_step
  ))

  toolbox.register("evaluate", evalSymbReg, points=testPoints)
  toolbox.register("select", tools.selTournament, tournsize=3)

  # Create statistics methods
  stats_error = tools.Statistics(lambda ind: ind.fitness.values)
  stats_size = tools.Statistics(len)

  mstats = tools.MultiStatistics(error=stats_error, size=stats_size)
  mstats.register("avg", np.mean)
  mstats.register("std", np.std)
  mstats.register("min", np.min)
  mstats.register("max", np.max)

  # Run the evoluationary algorithm
  pop = toolbox.population(n=args.number_of_individuals)
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

  # Define funcitons for recording output
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

  def writeEquation(individiual, output_name):
    with open(output_name, "w") as f:
      f.write(str(individiual))

  def plotEquationResults(individual, points, output_name):
    # Make all the lines
    func = toolbox.compile(expr=individual)
   
    if args.trojan_creation:
      lineLabel = "Evolved Trojan"
    else:
      lineLabel = "Evolved Benign"
 
    plt.plot(points, [func(x) for x in points], 'r',
       label=lineLabel
    )
   
    if args.trojan_creation:
      lineLabel = "Malware"
    else:
      lineLabel = "Actual Benign"

    plt.plot(points,
      [compiledTargetEquation(x) for x in points], 'g--',
      label=lineLabel
    )

    if args.trojan_creation:
      lineLabel = "Benign"
    else:
      lineLabel = "Evolved Trojan"

    plt.plot(points,
      [compiledStartingEquation(x) for x in points], 'k--',
      label=lineLabel
    )

    if args.trojan_creation:
      plt.plot(points, [pieceWiseFunction(x) for x in points],
       'b--', label="Piecewise Trojan"
      )

    # Make the legend
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2,
      mode="expand", borderaxespad=0.
    )
    # Save the figure
    plt.savefig(output_name)
    # Close the figure
    plt.close()

  # Create output directory
  outputDirectory = "output"
  if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

  # Determine if we were creating or removing a trojan
  if args.trojan_creation:
    programTypeName = "Creation"
  else:
    programTypeName = "Removal"

  # Output the results
  for individualN in range(len(hof)):  
    plotEquationStructure(
      hof[individualN],
      "{}/Trojan{}--halloffame-{}--equation_structure.png".format(
        outputDirectory,
        programTypeName,
        individualN
      )
    )
    plotEquationResults(
      hof[individualN],
      testPoints,
      "{}/Trojan{}--halloffame-{}--equation_results.png".format(
        outputDirectory,
        programTypeName,
        individualN
      )
    )
    writeEquation(
      hof[individualN],
      "{}/Trojan{}--halloffame-{}--equation_written.txt".format(
        outputDirectory,
        programTypeName,
        individualN
      )
    )

  return hof


if __name__ == "__main__":
  args = processArguments()

  runEvolution(args)


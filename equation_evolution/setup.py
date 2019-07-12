import numpy as np
import operator
from .primitives import pset
from deap import base, creator, gp, tools

def setup(benignEquation, malwareEquation, fitnessWeight, mutationSubTreeHeightMin,
        mutationSubTreeHeightMax, maxTreeHeight, testPointsStart, testPointsStop,
        testPointsStep, insertionStart, insertionStop):
    creatorSetup(fitnessWeight)
    toolboxSetup(benignEquation, malwareEquation, mutationSubTreeHeightMin,
        mutationSubTreeHeightMax, maxTreeHeight, testPointsStart, testPointsStop,
        testPointsStep, insertionStart, insertionStop
    )

def creatorSetup(fitnessWeight):
  # Create a custom type
  creator.create("FitnessMin", base.Fitness,
     weights=(fitnessWeight,)
  )
  creator.create("Individual", gp.PrimitiveTree,
    fitness=creator.FitnessMin, pset=pset
  )

def toolboxSetup(benignEquation, malwareEquation,  mutationSubTreeHeightMin,
        mutationSubTreeHeightMax, maxTreeHeight, testPointsStart, testPointsStop,
        testPointsStep, insertionStart, insertionStop):
  # Create an emtpy toolbox
  toolbox = base.Toolbox()
  


  # Define creation of the equations
  toolbox.register("manualEquation", gp.PrimitiveTree.from_string,
    pset=pset
  )
  benignEquationPrimitiveTree = toolbox.manualEquation(benignEquation)
  malwareEquationPrimitiveTree = toolbox.manualEquation(malwareEquation)
  
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
     min_=mutationSubTreeHeightMin,
     max_=mutationSubTreeHeightMax
  )
  toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut,
    pset=pset
  )

  toolbox.decorate("mate",
    gp.staticLimit(key=operator.attrgetter("height"),
    max_value=maxTreeHeight)
  )
  toolbox.decorate("mutate",
    gp.staticLimit(key=operator.attrgetter("height"),
    max_value=maxTreeHeight)
  )

  # Define equation compiling
  toolbox.register("compile", gp.compile, pset=pset)

  # Create the array of points that will be used for test
  testPoints = np.array(np.arange(
    testPointsStart,
    testPointsStop,
    testPointsStep
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
  toolbox.register("benignEquation", benignEquationCompiled)
  malwareEquationCompiled = toolbox.compile(malwareEquationPrimitiveTree)
  toolbox.register("malwareEquation", malwareEquationCompiled)
  toolbox.register("pieceWiseFunction", pieceWiseFunction,
          benignEquation=toolbox.benignEquation, malwareEquation=toolbox.malwareEquation,
          insertionStart=insertionStart, insertionStop=insertionStop
  )
 
  # Set selection method
  toolbox.register("select", tools.selTournament, tournsize=3)

  return toolbox


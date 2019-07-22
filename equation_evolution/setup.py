import numpy as np
import operator
import random
from .primitives import pset
from functools import partial
from deap import base, creator, gp, tools


def creatorSetup(fitnessWeight):
  # Create a custom type
  creator.create("FitnessMin", base.Fitness,
     weights=(fitnessWeight,)
  )
  creator.create("DirectIndividual", gp.PrimitiveTree,
    fitness=creator.FitnessMin, pset=pset
  )
      
  creator.create("GaussianIndividual", list, fitness=creator.FitnessMin)


def toolboxSetup(benignEquation, malwareEquation, testPointsStart, testPointsStop, testPointsStep, insertionStart, insertionStop):
  # Create an emtpy toolbox
  toolbox = base.Toolbox()

  toolbox.register("manualEquation", gp.PrimitiveTree.from_string,
    pset=pset
  )
  benignEquationPrimitiveTree = toolbox.manualEquation(benignEquation)
  toolbox.register("benignEquationPrimitiveTree", lambda: benignEquationPrimitiveTree)
  malwareEquationPrimitiveTree = toolbox.manualEquation(malwareEquation)
  toolbox.register("malwareEquationPrimitiveTree", lambda: malwareEquationPrimitiveTree)
  # Define equation compiling
  toolbox.register("compile", gp.compile, pset=pset)
  benignEquationCompiled = toolbox.compile(benignEquationPrimitiveTree)
  toolbox.register("benignEquation", benignEquationCompiled)
  malwareEquationCompiled = toolbox.compile(malwareEquationPrimitiveTree)
  toolbox.register("malwareEquation", malwareEquationCompiled)
  def pieceWiseFunction(x, benignEquation, malwareEquation, insertionStart, insertionStop):
    if insertionStart <= x <= insertionStop:
      return malwareEquation(x)
    else:
      return benignEquation(x)
  toolbox.register("pieceWiseFunction", pieceWiseFunction,
          benignEquation=toolbox.benignEquation, malwareEquation=toolbox.malwareEquation,
          insertionStart=insertionStart, insertionStop=insertionStop
  )

  # Create the array of points that will be used for test
  testPoints = np.array(np.arange(
    testPointsStart,
    testPointsStop,
    testPointsStep
  ))
  toolbox.register("testPoints", lambda: testPoints)

  # Define evaluation
  def evalSymbReg(individualFunction, targetFunction, points):
    # Evaluate the mean squared errors
    errors = np.power(
               np.subtract(
                 np.fromiter(map(individualFunction, points), np.float_),
                 np.fromiter(map(targetFunction, points),
                    np.float_
                 )
               ), 
               2
             )
    # Return average mean squared error
    return np.mean(errors),
  toolbox.register("generalEvalSymbReg", evalSymbReg)

  # Set selection method
  toolbox.register("select", tools.selTournament, tournsize=3)
  
  # Return the created toolbox
  return toolbox

def toolboxDirectSetup(benignEquation, malwareEquation, mutationSubTreeHeightMin,
        mutationSubTreeHeightMax, maxTreeHeight, testPointsStart, testPointsStop,
        testPointsStep, insertionStart, insertionStop):
  toolbox = toolboxSetup(benignEquation, malwareEquatio, ntestPointsStart, testPointsStop, testPointsStep, insertionStart, insertionStop) 


  # Define creation of the equations
  
  # Define creation of indiviuals for the  population
  toolbox.register("individual", tools.initIterate, creator.DirectIndividual, 
          lambda: toolbox.benignEquationPrimitiveTree()
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

  def compiledIndivdualEvalSymbReg(individual, targetFunction, points):
    # Transform the tree expression in a callable function
    compiledIndivdual = toolbox.compile(expr=individual)
    return toolbox.generalEvalSymbReg(compiledIndivdual, targetFunction, points)

  toolbox.register("evalSymbReg", compiledIndividualEvalSymbReg, points=toolbox.testPoints())

  return toolbox


def toolboxGaussianSetup(benignEquation, malwareEquation, mutationSubTreeHeightMin, mutationSubTreeHeightMax, maxTreeHeight,
        testPointsStart, testPointsStop, testPointsStep, insertionStart, insertionStop, initialValueRangeStart, initialValueRangeStop):
  if initialValueRangeStart == 0 and initialValueRangeStop == 0:
      raise ValueError("The range of initial values can't be restricted  to just 0")

  toolbox = toolboxSetup(benignEquation, malwareEquation, testPointsStart, testPointsStop, testPointsStep, insertionStart, insertionStop)

  def randomAorB():
      return random.randrange(initialValueRangeStart, initialValueRangeStop)
  
  def randomC():
      c = random.randrange(initialValueRangeStart, initialValueRangeStop)
      while c == 0:
        c = random.randrange(initialValueRangeStart, initialValueRangeStop)
      return c

  def randomGaussian():
    return [randomAorB(), randomAorB(), randomC(), toolbox.benignEquationPrimitiveTree()]

  toolbox.register("individual", tools.initIterate, creator.GaussianIndividual, 
          randomGaussian
  )
  toolbox.register("population", tools.initRepeat, list,
          toolbox.individual
  )

  toolbox.register("expr_mut", gp.genFull,
     min_=mutationSubTreeHeightMin,
     max_=mutationSubTreeHeightMax
  )
  toolbox.register("treeMutate", gp.mutUniform, expr=toolbox.expr_mut,
    pset=pset
  )
  toolbox.decorate("treeMutate",
    gp.staticLimit(key=operator.attrgetter("height"),
    max_value=maxTreeHeight)
  )
  def mutate(gaussian):
    choice = random.randrange(0,len(gaussian),1)
    change = random.randrange(-3,3)
    if choice < 2:
      gaussian[choice] += change
    elif choice == 2:
      newC = gaussian[choice] + change
      while newC == 0:
        change = random.randrange(-3,3)
        newC = gaussian[choice] + change
      gaussian[choice] = newC
    elif choice == 3:
      gaussian[choice] = toolbox.treeMutate(gaussian[choice])[0]
    else:
      raise ValueError("Illegal mutation choice: {}".format(choice))

    return gaussian,

  toolbox.register("mutate", mutate)

  toolbox.register("treeMate", gp.cxOnePoint)

  toolbox.decorate("treeMate",
    gp.staticLimit(key=operator.attrgetter("height"),
    max_value=maxTreeHeight)
  )
  def mate(gaussian1, gaussian2):
    if gaussian1[0] != gaussian2[0]:
        newA1 = random.randrange(min(gaussian1[0], gaussian2[0]), max(gaussian1[0], gaussian2[0]))
        newA2 = random.randrange(min(gaussian1[0], gaussian2[0]), max(gaussian1[0], gaussian2[0]))
        gaussian1[0] = newA1
        gaussian2[0] = newA2

    if gaussian1[1] != gaussian2[1]:
        newB1 = random.randrange(min(gaussian1[1], gaussian2[1]), max(gaussian1[1], gaussian2[1]))
        newB2 = random.randrange(min(gaussian1[1], gaussian2[1]), max(gaussian1[1], gaussian2[1]))
        gaussian1[1] = newB1
        gaussian2[1] = newB2

    if gaussian1[2] == 0 and gaussian2[2] == 0:
        raise ValueError("value of c can not be restricted to 0")
    elif gaussian1[2] != gaussian2[2]:
        def nonZeroC():
          newC = random.randrange(min(gaussian1[2], gaussian2[2]), max(gaussian1[2], gaussian2[2]))
          # We must have a non-zero value, so try again until we get that. 
          while newC == 0:
            newC = random.randrange(min(gaussian1[2], gaussian2[2]), max(gaussian1[2], gaussian2[2]))
          return newC
        newC1 = nonZeroC()
        newC2 = nonZeroC()
        gaussian1[2] = newC1
        gaussian2[2] = newC2
    
    gaussian1[3], gaussian2[3] = toolbox.treeMate(gaussian1[3], gaussian2[3])

    return gaussian1, gaussian2

  toolbox.register("mate", mate)

  def gaussianFunction(a, b, c, points):
      return np.multiply(
              a,
              np.exp(np.divide(
                  np.negative(np.power(
                      np.subtract(
                          points,
                          b),
                      2)),
                  np.multiply(
                      2,
                      np.power(c,2))
                  )),
              )

  def compileGaussianIndividual(individual):
      compiledPrimitives = toolbox.compile(individual[3])
      compiledGaussianFunction = partial(gaussianFunction, individual[0], individual[1], individual[2])

      def compiledWhole(x):
          return np.multiply(compiledGaussianFunction(x), compiledPrimitives(x))

      return compiledWhole

  toolbox.register("compileGaussianIndividual", compileGaussianIndividual)

  def gaussianTrojan(individual, benignEquation):
        compiledIndividual = toolbox.compileGaussianIndividual(individual)
        return lambda x: benignEquation(x) + compiledIndividual(x)
  toolbox.register("gaussianTrojan", gaussianTrojan)

  def gaussianEvalSymbReg(individual, targetFunction, points):
    trojan = toolbox.gaussianTrojan(individual, toolbox.benignEquation)

    return toolbox.generalEvalSymbReg(trojan, targetFunction, points)

  toolbox.register("evalSymbReg", gaussianEvalSymbReg, points=toolbox.testPoints())

  return toolbox


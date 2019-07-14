import random
from deap import algorithms, tools

def evolveUntilCondition(toolbox, population, hallOfFame, mutationProb, crossOverProb, stats, stoppingCondition, maxNumberOfGenerations, verbose=False):
  logbook = tools.Logbook()
  logbook.header = ['gen', 'nevals'] + stats.fields

  # Evalutate the individuals with an invalid fitness
  invalid_ind = [ind for ind in population if not ind.fitness.valid]
  fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
  for ind, fit in zip(invalid_ind, fitnesses):
      ind.fitness.values = fit

  hallOfFame.update(population)
  record = stats.compile(population)
  logbook.record(gen=0, nevals=len(invalid_ind), **record)
  if verbose:
    print(logbook.stream)

  # Begin the generational process
  gen = 1
  while gen < maxNumberOfGenerations and not stoppingCondition(population, hallOfFame):
      # Select the next generation individuals
      offspring = toolbox.select(population, len(population))

      # Vary the pool of individuals
      offspring = algorithms.varAnd(offspring, toolbox, crossOverProb, mutationProb)

      # Evaluate the individuals with an invalid fitness (were modified)
      invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
      fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
      for ind, fit in zip(invalid_ind, fitnesses):
          ind.fitness.values = fit

      # Update the hall of fame with the generated individuals
      hallOfFame.update(offspring)

      # Replace the current population by the offspring
      population[:] = offspring

      # Append the current generation statistics to the logbook
      record = stats.compile(population)
      logbook.record(gen=gen, nevals=len(invalid_ind), **record)
      if verbose:
        print(logbook.stream)

      # Increase generation number
      gen += 1

  return hallOfFame, population, gen, logbook, random.getstate()


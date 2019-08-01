import numpy as np
from deap import tools

stats_error = tools.Statistics(lambda ind: ind.fitness.values)
stats_size = tools.Statistics(len)

mstats = tools.MultiStatistics(error=stats_error, size=stats_size)
mstats.register("avg", np.mean)
mstats.register("std", np.std)
mstats.register("min", np.min)
mstats.register("max", np.max)

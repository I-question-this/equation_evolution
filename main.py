#!/usr/bin/env python3
"""Driver program for equation_evolution.
Using the toolbox and mstats defined equation_evolution.definations
the evolutionary process is run.
"""
from equation_evolution.evolution import evolve

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

  pop, log, hof, toolbox = evolve(100, 1000, 0.5, 0.1, testPoints)
  
  toolbox.plotEquationStructure(hof[0], "halloffame--equation_structure.png")
  toolbox.plotEquationResults(hof[0], testPoints, "halloffame--equation_results.png")


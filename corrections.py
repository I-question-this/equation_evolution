#!/usr/bin/env python3
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
from sys import argv

fileName = argv[1]
print(fileName)

creator.create("FitnessMin", base.Fitness,
   weights=(-2.0,)
)
creator.create("Individual", gp.PrimitiveTree,
  fitness=creator.FitnessMin, pset=pset
)

with open(fileName, "rb") as fileIn:
    results = pickle.load(fileIn)
    results["version"] = 1.0
    results["creation"]["targetError"] = 0.05
    results["removal"]["targetError"] = 0.0
    results["testPoints"] = {"start": -2, "stop": 2.25, "step": 0.25}
    results["insertion"] = {"start": -1.0, "stop": 1.0}

with open(fileName, "wb") as fileOut:
    pickle.dump(results, fileOut)


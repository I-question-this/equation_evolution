#!/usr/bin/env python3
import argparse
import matplotlib.pyplot as plt
import numpy as np
import operator
import os
import pickle
import pygraphviz as pgv
from equation_evolution.setup import creatorSetup
from functools import partial
from sys import argv

outputDirectory = "output"

creatorSetup(-2.0)

gensUsed = []
gensAllowed = []

for subDir, dirs, files in os.walk(outputDirectory):
    for fileName in files:
        if not fileName.endswith(".pickle"):
            # It's not a pickle file, so skip it
            continue
    
        filePath = os.path.join(subDir, fileName)
        with open(filePath, "rb") as fileIn:
            results = pickle.load(fileIn)
            gensUsed.append(results["removal"]["generationsUsed"])
            gensAllowed.append(results["removal"]["maximumGenerationsAllowed"])

print("Max Generations Used: {}".format(max(gensUsed)))
print("Min Generations Used: {}".format(min(gensUsed)))
print("Average Generations Used: {}".format(np.mean(gensUsed)))
print("Average Ratio of Generations Used: {}".format(np.mean([used/allowed for used, allowed in zip(gensUsed, gensAllowed)]))) 


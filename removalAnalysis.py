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

removals = []

for subDir, dirs, files in os.walk(outputDirectory):
    for fileName in files:
        if not fileName.endswith(".pickle"):
            # It's not a pickle file, so skip it
            continue
    
        filePath = os.path.join(subDir, fileName)
        with open(filePath, "rb") as fileIn:
            results = pickle.load(fileIn)
            # Addresses an index error in the code, it caused a "off by one" error
            results["removal"]["generationsUsed"] = min(results["removal"]["maximumGenerationsAllowed"], results["removal"]["generationsUsed"])
            removals.append(results["removal"])


print("Max Generations Used: {}".format(max(results["generationsUsed"] for results in removals)))
print("Min Generations Used: {}".format(min(results["generationsUsed"] for results in removals)))
print("Average Generations Used: {}".format(np.mean([results["generationsUsed"] for results in removals])))
print("Average Ratio of Generations Used: {}".format(np.mean([results["generationsUsed"]/results["maximumGenerationsAllowed"] for results in removals]))) 


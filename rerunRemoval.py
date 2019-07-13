#!/usr/bin/env python3
import argparse
import matplotlib.pyplot as plt
import numpy as np
import operator
import os
import pickle
import pygraphviz as pgv
import subprocess
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
        # Rerun, but skipping the creation phase
        subprocess.run(
          [
             "./main.py",
             results["benignEquation"],
             results["benignEquationType"],
             results["malwareEquation"],
             results["malwareEquationType"],
             "--output_name",
             filePath,
             "--verbose",
             "--max_number_of_generations",
             str(results["removal"]["maximumGenerationsAllowed"]),
             "--redoRemovalPickle",
             filePath
          ]
        )


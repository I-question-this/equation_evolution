#!/usr/bin/env python3
import argparse
import matplotlib.pyplot as plt
import numpy as np
import operator
import os
import pickle
import pygraphviz as pgv
from deap import creator, gp
from equation_evolution.primitives import pset
from equation_evolution.setup import creatorSetup
from functools import partial
from sys import argv

outputDirectory = "output"

creatorSetup(-2.0)

allResults = []

for subDir, dirs, files in os.walk(outputDirectory):
    for fileName in files:
        if not fileName.endswith(".pickle"):
            # It's not a pickle file, so skip it
            continue
    
        filePath = os.path.join(subDir, fileName)
        with open(filePath, "rb") as fileIn:
            results = pickle.load(fileIn)
            # Addresses an index error in the code, it caused a "off by one" error
            results["removal"]["generationsUsed"] = min(results["removal"]["maximumGenerationsAllowed"],
                      results["removal"]["generationsUsed"]
                    )
            results["creation"]["generationsUsed"] = min(results["creation"]["maximumGenerationsAllowed"],
                      results["creation"]["generationsUsed"]
                    )
            allResults.append(results)

def crossAnalysis():
    print("Analysis: Cross")

    sizeRatios = []
    for result in allResults:
        evolvedCreation = result["creation"]["hallOfFame"][0]
        if type(evolvedCreation) == creator.DirectIndividual:
            evolvedCreationLength = len(evolvedCreation)
        elif type(evolvedCreation) == creator.GaussianIndividual:
            evolvedCreationLength = len(evolvedCreation[3])
        else:
            raise ValueError("Unknown type: {}".format(type(evolvedCreation)))

        evolvedRemoval = result["removal"]["hallOfFame"][0]
        if type(evolvedRemoval) == creator.DirectIndividual:
            evolvedRemovalLength = len(evolvedRemoval)
        elif type(evolvedRemoval) == creator.GaussianIndividual:
            evolvedRemovalLength = len(evolvedRemoval[3])
        else:
            raise ValueError("Unknown type: {}".format(type(evolvedRemoval)))

        sizeRatios.append(np.divide(evolvedRemovalLength, evolvedCreationLength))

    print("Average of Removal/Creation: {}".format(np.mean(sizeRatios)))

def modeSpecificAnalysis(mode):
    print("Analysis: {}".format(mode.capitalize()))
    print("Average Fitness: {}".format(np.mean(results[mode]["hallOfFame"][0].fitness.values[0])))
    print("Max Generations Used: {}".format(max(results[mode]["generationsUsed"]
        for results in allResults)
    ))
    print("Min Generations Used: {}".format(min(results[mode]["generationsUsed"]
        for results in allResults)
    ))
    print("Average Generations Used: {}".format(np.mean([results[mode]["generationsUsed"]
        for results in allResults])
    ))
    print("Average Ratio of Generations Used: {}".format(
        np.mean([results[mode]["generationsUsed"]/results[mode]["maximumGenerationsAllowed"]
            for results in allResults])
    ))

    sizeRatios = []
    for result in allResults:
        evolved = result[mode]["hallOfFame"][0]
        if type(evolved) == creator.DirectIndividual:
            evolvedLength = len(evolved)
        elif type(evolved) == creator.GaussianIndividual:
            evolvedLength = len(evolved[3])
        else:
            raise ValueError("Unknown type: {}".format(type(evolved)))

        originalLength = len(gp.PrimitiveTree.from_string(result["benignEquation"], pset))
        sizeRatios.append(np.divide(evolvedLength, originalLength))

    print("Average {}/Benign: {}".format(mode.capitalize(), np.mean(sizeRatios)))
    
    def removeNumbers(string):
        return ''.join(c for c in string if not c.isdigit())

    types = {}
    for result in allResults:
      typeKey = "{}->{}".format(
              removeNumbers(result["malwareEquationType"]),
              removeNumbers(result["benignEquationType"])
      )

      if types.get(typeKey) is None:
          types[typeKey] = {"averageGensUsed": None, "results": list()}
      types[typeKey]["results"].append(result)

    for typeKey in types.keys():
      types[typeKey]["averageGensUsed"] = np.mean([r[mode]["generationsUsed"] for r in types[typeKey]["results"]])

    sortedByAverageGensUsed = sorted(list(types.keys()), key=lambda typeKey: types[typeKey]["averageGensUsed"])
    xs = np.arange(len(types))
    plt.bar(xs, [types[typeKey]["averageGensUsed"] for typeKey in sortedByAverageGensUsed], zorder=-1)
    for typeKey, x in zip(sortedByAverageGensUsed, xs):
        for result in types[typeKey]["results"]:
          if result[mode]["generationsUsed"] == result[mode]["maximumGenerationsAllowed"]:
            color="r"
          elif result[mode]["generationsUsed"] == 1:
            color="g"
          else:
            color="k"
          plt.scatter([x], result[mode]["generationsUsed"], color=color)

    plt.title("Generations Used -- {}".format(mode))
    plt.xlabel("Malware -> Benign")
    plt.xticks(xs,
            list(types.keys()),
            rotation='vertical'
    )
    plt.ylabel("Num. Gens. Used")
    plt.yticks(np.arange(0,2000,250))
    plt.grid()

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*len(allResults)+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin, bottom=0.4)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    plt.savefig(os.path.join("presentationOutput", "{}_generations_used.png".format(mode)))
    plt.close()

modeSpecificAnalysis("creation")
modeSpecificAnalysis("removal")
crossAnalysis()


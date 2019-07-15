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

def analysis(mode):
    print("Analysis: {}".format(mode))
    print("Max Generations Used: {}".format(max(results[mode]["generationsUsed"]
        for results in allResults))
    )
    print("Min Generations Used: {}".format(min(results[mode]["generationsUsed"]
        for results in allResults))
    )
    print("Average Generations Used: {}".format(np.mean([results[mode]["generationsUsed"]
        for results in allResults]))
    )
    print("Average Ratio of Generations Used: {}".format(
        np.mean([results[mode]["generationsUsed"]/results[mode]["maximumGenerationsAllowed"]
            for results in allResults]))
    ) 
    
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

    plt.savefig("{}_generations_used.png".format(mode))
    plt.close()

analysis("creation")
analysis("removal")


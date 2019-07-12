#!/usr/bin/env python3
"""Runs the main program multiple times with different equations
"""
import argparse
import datetime
import numpy as np
import os
import pickle
import subprocess
from deap import gp
from equation_evolution.output import plotTrojanCreation, plotTrojanRemoval
from equation_evolution.setup import creatorSetup, toolboxSetup

outputDirectory = "output"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

equations = {
        "large1": "div(pow(sin(cos(sub(mul(pow(mul(sub(0.0, 1.0), pow(1.0, 0.0)), div(sub(x, x), pow(x, 0.0))), neg(div(div(1.0, x), add(0.0, 0.0)))), pow(mul(sub(cos(x), sin(-1.0)), sin(sin(x))), mul(div(add(-1.0, x), add(x, x)), mul(div(x, x), cos(0.0))))))), pow(sin(sub(sub(sub(neg(div(0.0, x)), sin(cos(1.0))), sin(neg(sin(-1.0)))), div(pow(add(mul(x, 1.0), sin(-1.0)), pow(div(x, 1.0), pow(x, 1.0))), add(sin(neg(x)), mul(cos(x), cos(x)))))), sin(sub(mul(neg(sin(sub(x, 0.0))), add(sub(sub(x, -1.0), sub(0.0, 1.0)), pow(neg(1.0), sin(-1.0)))), sub(pow(sin(cos(x)), add(sin(0.0), mul(0.0, x))), neg(div(pow(0.0, 0.0), sin(0.0)))))))), neg(sub(cos(cos(cos(sub(cos(div(x, x)), sub(div(-1.0, x), neg(1.0)))))), sin(sub(mul(sub(sin(neg(0.0)), sub(add(x, x), neg(x))), cos(div(mul(0.0, 0.0), add(1.0, x)))), sin(pow(sin(pow(x, 0.0)), add(sin(x), sub(x, -1.0)))))))))", 
        "large2": "div(sub(sin(div(add(mul(add(pow(-1.0, x), pow(x, x)), div(pow(1.0, 1.0), sub(x, x))), mul(sin(sin(x)), cos(sub(x, x)))), add(neg(cos(pow(x, x))), add(sin(div(1.0, x)), mul(div(1.0, 0.0), mul(x, 0.0)))))), sub(mul(cos(mul(add(sin(x), neg(x)), sub(sub(x, 1.0), neg(x)))), neg(sub(pow(sin(x), pow(0.0, x)), pow(pow(1.0, -1.0), add(0.0, x))))), cos(neg(sin(cos(div(-1.0, x))))))), add(pow(cos(cos(div(neg(cos(x)), cos(cos(1.0))))), sub(mul(cos(pow(mul(x, 0.0), pow(x, 1.0))), sin(pow(pow(x, x), pow(1.0, 0.0)))), neg(mul(mul(mul(x, 1.0), div(x, x)), sin(mul(x, x)))))), div(div(add(sub(cos(cos(-1.0)), mul(mul(-1.0, x), sub(x, -1.0))), sub(add(sub(x, 1.0), cos(1.0)), cos(neg(x)))), div(sin(neg(neg(1.0))), add(mul(mul(-1.0, x), neg(-1.0)), cos(sub(x, 1.0))))), cos(sin(neg(mul(sin(x), neg(x))))))))",
        "exponential1": "pow(add(1,1),x)",
        "exponential2": "pow(add(1,1),add(x,1))",
        "linear1": "x",
        "linear2": "add(x,1)",
        "polynomial1": "pow(x,1)",
        "polynomial2": "pow(x,add(1,1))",
        "reciprocal1": "div(1,x)",
        "reciprocal2": "div(add(1,1),x)",
        "root1": "pow(x,div(1,add(1,1)))",
        "root2": "pow(x,div(1,add(add(1,1),1)))",
        "sin1": "sin(x)",
        "sin2": "sin(add(x,1))",
        "cos1": "cos(x)",
        "cos2": "cos(add(x,1)"
}


def runEvolution():
    for benignEquationName, benignEquation in equations.items():
        for malwareEquationName, malwareEquation in equations.items():
            if benignEquationName == malwareEquationName:
                continue
            # Run evolving the Trojan
            subprocess.run(
                [
                    "./main.py",
                    benignEquation,
                    malwareEquation,
                    "--output_name",
                    os.path.join(outputDirectory,
                        "{}-{}-{}.pickle".format(
                            benignEquationName,
                            malwareEquationName,
                            str(datetime.datetime.now()).replace(" ", "_")
                        )
                    ),
                    "--verbose",
                    "--max_number_of_generations",
                    str(args.max_number_of_generations),
                ]
            )


def produceOutputs():
    creatorSetup(-2.0)
    for subDir, dirs, files in os.walk(outputDirectory):
        for fileName in files:
            if not fileName.endswith(".pickle"):
                # It's not a pickle file, so skip it
                continue
            filePath = os.path.join(subDir, fileName)
            with open(filePath, "rb") as fileIn:
                results = pickle.load(fileIn)

            if results["version"] > 1.0:
                print("{} -- Unsupported version: {}".format(fileName, results["version"]))
                continue

            benignName = fileName.split('-')[0]
            malwareName = fileName.split('-')[1]
            toolbox = toolboxSetup(equations[benignName], equations[malwareName],
                1, 3, 17, results["testPoints"]["start"], results["testPoints"]["stop"],
                results["testPoints"]["step"], results["insertion"]["start"], 
                results["insertion"]["stop"]
            )
            points = np.array(np.arange(
                results["testPoints"]["start"],
                results["testPoints"]["stop"],
                results["testPoints"]["step"]
            ))
            plotTrojanCreation(toolbox.benignEquation, toolbox.malwareEquation,
                toolbox.pieceWiseFunction,
                toolbox.compile(results["creation"]["hallOfFame"][0]),
                points, results["insertion"]["start"], results["insertion"]["stop"],
                filePath.replace("pickle", "trojanCreation.png")
            )
            plotTrojanRemoval(toolbox.benignEquation, toolbox.malwareEquation,
                toolbox.compile(results["creation"]["hallOfFame"][0]),
                toolbox.compile(results["removal"]["hallOfFame"][0]),
                points, results["insertion"]["start"], results["insertion"]["stop"],
                filePath.replace("pickle", "trojanRemoval.png")
            )
            # produceLaTeXFigures()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_evolution", action="store_true", default=True,
            help="Rather to run the evolution or not. Default is True"
        )
    parser.add_argument("--max_number_of_generations", type=int, default=2000,
            help="The maximum number of generations. Default is 2000"
    )
    args = parser.parse_args()

    if not args.skip_evolution:
        runEvolution()
    produceOutputs()


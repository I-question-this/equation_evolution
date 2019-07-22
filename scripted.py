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
from functools import partial
from equation_evolution.output import plotTrojanCreation, plotTrojanRemoval
from equation_evolution.setup import creatorSetup, toolboxDirectSetup, toolboxGaussianSetup

outputDirectory = "output"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

equations = {
        "large1": "div(pow(sin(cos(sub(mul(pow(mul(sub(0.0, 1.0), pow(1.0, 0.0)), div(sub(x, x), pow(x, 0.0))), neg(div(div(1.0, x), add(0.0, 0.0)))), pow(mul(sub(cos(x), sin(-1.0)), sin(sin(x))), mul(div(add(-1.0, x), add(x, x)), mul(div(x, x), cos(0.0))))))), pow(sin(sub(sub(sub(neg(div(0.0, x)), sin(cos(1.0))), sin(neg(sin(-1.0)))), div(pow(add(mul(x, 1.0), sin(-1.0)), pow(div(x, 1.0), pow(x, 1.0))), add(sin(neg(x)), mul(cos(x), cos(x)))))), sin(sub(mul(neg(sin(sub(x, 0.0))), add(sub(sub(x, -1.0), sub(0.0, 1.0)), pow(neg(1.0), sin(-1.0)))), sub(pow(sin(cos(x)), add(sin(0.0), mul(0.0, x))), neg(div(pow(0.0, 0.0), sin(0.0)))))))), neg(sub(cos(cos(cos(sub(cos(div(x, x)), sub(div(-1.0, x), neg(1.0)))))), sin(sub(mul(sub(sin(neg(0.0)), sub(add(x, x), neg(x))), cos(div(mul(0.0, 0.0), add(1.0, x)))), sin(pow(sin(pow(x, 0.0)), add(sin(x), sub(x, -1.0)))))))))", 
        "large2": "div(sub(sin(div(add(mul(add(pow(-1.0, x), pow(x, x)), div(pow(1.0, 1.0), sub(x, x))), mul(sin(sin(x)), cos(sub(x, x)))), add(neg(cos(pow(x, x))), add(sin(div(1.0, x)), mul(div(1.0, 0.0), mul(x, 0.0)))))), sub(mul(cos(mul(add(sin(x), neg(x)), sub(sub(x, 1.0), neg(x)))), neg(sub(pow(sin(x), pow(0.0, x)), pow(pow(1.0, -1.0), add(0.0, x))))), cos(neg(sin(cos(div(-1.0, x))))))), add(pow(cos(cos(div(neg(cos(x)), cos(cos(1.0))))), sub(mul(cos(pow(mul(x, 0.0), pow(x, 1.0))), sin(pow(pow(x, x), pow(1.0, 0.0)))), neg(mul(mul(mul(x, 1.0), div(x, x)), sin(mul(x, x)))))), div(div(add(sub(cos(cos(-1.0)), mul(mul(-1.0, x), sub(x, -1.0))), sub(add(sub(x, 1.0), cos(1.0)), cos(neg(x)))), div(sin(neg(neg(1.0))), add(mul(mul(-1.0, x), neg(-1.0)), cos(sub(x, 1.0))))), cos(sin(neg(mul(sin(x), neg(x))))))))",
        "large3": "add(sub(add(x, cos(0.0)), mul(sub(add(sin(sin(0.0)), mul(x, pow(add(x, 1.0), pow(div(mul(neg(cos(sub(x, x))), 0.0), 0.0), cos(div(1.0, -1.0)))))), sin(div(x, cos(x)))), div(sub(cos(neg(sub(0.0, 0.0))), pow(add(cos(x), neg(-1.0)), -1.0)), x))), div(cos(x), pow(pow(sin(1.0), pow(mul(x, pow(cos(mul(x, x)), cos(cos(add(0.0, sub(sin(mul(-1.0, mul(0.0, 1.0))), add(x, -1.0))))))), div(mul(sin(x), mul(0.0, x)), cos(div(x, 0.0))))), add(cos(cos(add(add(x, neg(sin(pow(mul(add(add(sin(x), cos(add(cos(x), mul(x, x)))), x), mul(sin(x), x)), x)))), x))), div(div(div(mul(cos(0.0), sub(cos(sub(0.0, cos(add(x, sin(mul(1.0, x)))))), div(add(cos(sub(cos(x), cos(sin(div(1.0, x))))), cos(x)), sin(neg(x))))), x), pow(x, mul(add(sub(mul(add(sin(x), add(sin(div(x, x)), add(mul(pow(x, mul(x, x)), div(x, x)), 1.0))), pow(sub(x, sub(0.0, x)), mul(sub(x, cos(mul(x, x))), add(pow(x, sub(pow(x, 0.0), mul(-1.0, x))), neg(mul(-1.0, sub(1.0, 0.0))))))), div(div(add(cos(x), sub(1.0, x)), cos(cos(neg(0.0)))), sub(sub(x, cos(1.0)), mul(x, x)))), cos(div(x, -1.0))), sub(neg(neg(add(x, sin(-1.0)))), cos(x))))), x)))))",
        "exponential1": "pow(add(1,1),x)",
        "exponential2": "pow(add(1,1),add(x,1))",
        "exponential3": "pow(add(1,add(1,1)),add(x,add(1,1)))",
        "linear1": "x",
        "linear2": "add(x,1)",
        "linear3": "add(mul(add(1,add(1,1)),x),add(1,1))",
        "polynomial1": "pow(x,add(1,1))",
        "polynomial2": "pow(x,add(1,add(1,1)))",
        "polynomial3": "add(pow(x,add(1,add(1,1))),mul(add(1,1),pow(x,add(1,1))))",
        "reciprocal1": "div(1,x)",
        "reciprocal2": "div(add(1,1),x)",
        "reciprocal3": "sub(div(add(1,1),x),add(1,add(1,add(1,1))))",
        "root1": "pow(x,div(1,add(1,1)))",
        "root2": "pow(x,div(1,add(add(1,1),1)))",
        "root3": "pow(mul(add(1,1),x),div(1,add(add(1,1),1)))",
        "sin1": "sin(x)",
        "sin2": "sin(add(x,1))",
        "sin3": "mul(add(1,add(1,1)),sin(add(x,1)))",
        "cos1": "cos(x)",
        "cos2": "cos(add(x,1))",
        "cos3": "mul(add(1,add(1,1)),cos(add(x,1)))"
}


def runEvolution():
    for benignEquationName, benignEquation in equations.items():
        for malwareEquationName, malwareEquation in equations.items():
            if benignEquationName == malwareEquationName:
                continue
            for insertionStart, insertionStop in [(-1,1), (-0.5,0.5), (-0.25,0.25)]:
                # Run evolving the Trojan
                subprocess.run(
                    [
                        "./main.py",
                        benignEquation,
                        benignEquationName,
                        malwareEquation,
                        malwareEquationName,
                        "--output_name",
                        os.path.join(outputDirectory,
                            "{}-{}-{}-{}.pickle".format(
                                benignEquationName,
                                malwareEquationName,
                                insertionStart,
                                insertionStop
                            )
                        ),
                        "--verbose",
                        "--max_number_of_generations",
                        str(args.max_number_of_generations),
                        "--insertion_start",
                        str(insertionStart),
                        "--insertion_stop",
                        str(insertionStop),
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

            if results["version"] < 1.2:
                print("{} -- Unsupported version: {}".format(fileName, results["version"]))
                continue

            benignName = fileName.split('-')[0]
            malwareName = fileName.split('-')[1]
            if args.direct:
                toolbox = toolboxDirectSetup(results["benignEquation"], results["malwareEquation"],
                    1, 3, 17, results["testPoints"]["start"], results["testPoints"]["stop"],
                    results["testPoints"]["step"], results["insertion"]["start"], 
                    results["insertion"]["stop"]
                )
                plotTrojanCreation(toolbox.benignEquation, toolbox.malwareEquation,
                    toolbox.pieceWiseFunction,
                    toolbox.compile(results["creation"]["hallOfFame"][0]),
                    toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                    filePath.replace("pickle", "directTrojanCreation.png")
                )
                plotTrojanRemoval(toolbox.benignEquation, toolbox.malwareEquation,
                    toolbox.compile(results["creation"]["hallOfFame"][0]),
                    toolbox.compile(results["removal"]["hallOfFame"][0]),
                    toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                    filePath.replace("pickle", "directTrojanRemoval.png")
                )
            else:
                toolbox = toolboxGaussianSetup(results["benignEquation"], results["malwareEquation"],
                    1, 3, 17, results["testPoints"]["start"], results["testPoints"]["stop"],
                    results["testPoints"]["step"], results["insertion"]["start"], 
                    results["insertion"]["stop"], -3, 3
                )
                evolvedTrojan = toolbox.gaussianTrojan(results["creation"]["hallOfFame"][0], toolbox.benignEquation)
                plotTrojanCreation(toolbox.benignEquation, toolbox.malwareEquation,
                    toolbox.pieceWiseFunction,
                    evolvedTrojan,
                    toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                    filePath.replace("pickle", "directTrojanCreation.png")
                )
                evolvedBenign = toolbox.gaussianTrojan(results["removal"]["hallOfFame"][0], toolbox.benignEquation)
                plotTrojanRemoval(toolbox.benignEquation, toolbox.malwareEquation,
                    evolvedTrojan,
                    evolvedBenign,
                    toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                    filePath.replace("pickle", "directTrojanRemoval.png")
                )

def produceLaTeXListOfEquations():
    filePath = os.path.join("presentationOutput", "equationsList.tex")

    with open(filePath, "w") as fileOut:
        fileOut.write("\\begin{itemize}\n")
        for equationName in sorted(equations.keys()):
            fileOut.write("\item \\textbf{{{}:}} {}\n".format(equationName, equations[equationName]))
        fileOut.write("\end{itemize}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_evolution", action="store_true", default=False,
            help="Rather to run the evolution or not. Default is True"
        )
    parser.add_argument("--max_number_of_generations", type=int, default=2000,
            help="The maximum number of generations. Default is 2000"
    )
    parser.add_argument("--direct", action="store_true", default=False,
            help="Uses the direct manipluation of an equation instead of gausian"
    )
    args = parser.parse_args()

    if not args.skip_evolution:
        runEvolution()
    produceOutputs()
    produceLaTeXListOfEquations()

